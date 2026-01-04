import asyncio
import json
import time
import socket
import threading
from typing import Optional, Dict, Any, List

from routes.messagebus import bus
from routes.base_value import GW_IP, GW_TCP_PORT


class GatewayClient:
    """
    TCP client to OTA_GW with improved connection stability:
    - Fixed race conditions in connection handling
    - Proper cleanup of stale connections
    - Thread-safe connection state management
    """
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.ackseq: int = 0
        self.pending_tasks: List[Dict[str, Any]] = []
        self.connected: bool = False
        self.last_ack = 0
        self.conn_lock = asyncio.Lock()
        self.last_keepalive_ack = 0
        self.keepalive_ack_interval = 5  # seconds
        self._receiver_task: Optional[asyncio.Task] = None
        self._connection_id = 0  # Track connection instances

    async def run(self):
        """Main connection loop with auto-reconnect and TCP_NODELAY."""
        while True:
            connection_id = self._connection_id
            print(f"[Backend-TCP] Connection attempt #{connection_id}, connected={self.connected}")
            
            try:
                # Check if already connected
                async with self.conn_lock:
                    if self.connected and self.writer and not self.writer.is_closing():
                        print(f"[Backend-TCP] Already connected (#{connection_id}), skipping")
                        await asyncio.sleep(10)
                        continue
                
                # Establish new connection
                reader, writer = await asyncio.open_connection(self.ip, self.port)
                
                sock = writer.get_extra_info("socket")
                if sock:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                
                print(f"[Backend-TCP] TCP connection established (#{connection_id})")
                
                # Update connection state atomically
                async with self.conn_lock:
                    # Cancel any existing receiver
                    if self._receiver_task and not self._receiver_task.done():
                        self._receiver_task.cancel()
                        try:
                            await self._receiver_task
                        except asyncio.CancelledError:
                            pass
                    
                    # Close old writer if exists
                    if self.writer and not self.writer.is_closing():
                        try:
                            self.writer.close()
                            await self.writer.wait_closed()
                        except Exception:
                            pass
                    
                    self.reader = reader
                    self.writer = writer
                    self.connected = True
                    self.last_ack = time.time()
                    self._connection_id += 1
                    
                    print(f"[TCP_Async] Connected with GW (#{connection_id})")
                    
                    # Send hello handshake
                    hello_msg = {"msg_type": "hello", "role": "ota_server"}
                    writer.write((json.dumps(hello_msg) + "\n").encode())
                    await writer.drain()
                    
                    # Flush any pending tasks
                    await self._flush_pending()
                
                # Start receiver (outside lock to avoid blocking)
                await self.receiver(reader, writer, connection_id)
                    
            except asyncio.CancelledError:
                print(f"[TCP_Async] Connection task cancelled (#{connection_id})")
                break
            except Exception as e:
                print(f"[TCP_Async] Connection error (#{connection_id}): {e}")
            
            finally:
                # Cleanup
                async with self.conn_lock:
                    # Only cleanup if this is still the current connection
                    if connection_id == self._connection_id - 1:
                        self.connected = False
                        if self.writer:
                            try:
                                if not self.writer.is_closing():
                                    self.writer.close()
                                    await self.writer.wait_closed()
                            except Exception:
                                pass
                            self.writer = None
                        self.reader = None
                        print(f"[TCP_Async] Cleaned up connection (#{connection_id})")
                
                print(f"[TCP_Async] Disconnected from GW (#{connection_id}), retry in 10s")
                await asyncio.sleep(10)

    async def receiver(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, connection_id: int):
        """Receive messages from GW and publish to MessageBus."""
        try:
            print(f"[TCP_Async] Receiver started (#{connection_id})")
            while True:
                data = await reader.readline()
                if not data:
                    print(f"[TCP] GW disconnected (#{connection_id})")
                    break

                msg = data.decode(errors="replace").strip()
                if not msg:
                    continue

                try:
                    obj = json.loads(msg)
                except Exception as e:
                    print(f"[TCP] Parse error (#{connection_id}):", e, msg)
                    continue

                # Dispatch by msg_type
                mt = obj.get("msg_type")
                if mt == "keep_alive":
                    # Use the local writer parameter, not self.writer
                    await self._send_keepalive_ack(writer, obj, connection_id)
                    self.last_ack = time.time()
                    print(f'[TCP] Keepalive received (#{connection_id})')
                    
                elif mt == "ota_task_ack":
                    bus.publish("tcp.update_task", obj)
                    print(f"[TCP_Async] Rx task_ack from GW (#{connection_id})", obj)
                    
                elif mt == "register":
                    bus.publish("tcp.device_update", obj)
                    print(f"[Backend-TCP] Device registered (#{connection_id})")
                else:
                    print(f"[TCP] GW message (#{connection_id}):", obj)
                    
        except asyncio.CancelledError:
            print(f"[TCP_Async] Receiver cancelled (#{connection_id})")
            raise
        except Exception as e:
            print(f"[TCP_Async] Receiver error (#{connection_id}):", e)
        finally:
            print(f"[TCP_Async] Receiver exiting (#{connection_id})")

    async def _send_keepalive_ack(self, writer: asyncio.StreamWriter, obj: Dict[str, Any], connection_id: int):
        """Reply to keep_alive with ack using the provided writer."""
        # Rate limit keepalive acks
        now = time.time()
        if now - self.last_keepalive_ack < self.keepalive_ack_interval:
            return
        
        # Check if writer is still valid
        if writer.is_closing():
            print(f"[TCP_Async] Writer closed, skipping keepalive ack (#{connection_id})")
            return
        
        ack = {"msg_type": "keep_alive_ack"}
        try:
            writer.write((json.dumps(ack) + '\n').encode())
            await writer.drain()
            self.last_keepalive_ack = now
            print(f"[TCP_Async] Tx keepalive_ack (#{connection_id}): {self.last_keepalive_ack}")
        except Exception as e:
            print(f"[TCP_Async] Keepalive send failed (#{connection_id}):", e)

    async def send_task(self, filepath: str, task: Dict[str, Any]):
        """Send a task to GW. If not connected, buffer for later flush."""
        if not task or not isinstance(task, dict):
            print("[TCP] Invalid task payload:", task)
            return

        # Check connection state
        async with self.conn_lock:
            if not self.writer or self.writer.is_closing() or not self.connected:
                print("[TCP] GW not connected; buffering task")
                self.pending_tasks.append({"filepath": filepath, "task": task})
                return
            
            writer = self.writer

        # Send outside the lock
        payload_str = json.dumps(task) + "\n"
        try:
            writer.write(payload_str.encode())
            await writer.drain()
            print(f"[TCP] Sent task: {payload_str!r}")
        except Exception as e:
            print("[TCP] Send error, buffering task:", e)
            self.pending_tasks.append({"filepath": filepath, "task": task})
            return

        # Update status and publish sent event
        try:
            task["status"] = "success"
        except Exception:
            pass
        
        try:
            with open(filepath, "w") as f:
                json.dump(task, f, indent=2)
        except Exception as e:
            print("[TCP] Write file error:", e, filepath)

        bus.publish("task.sent", {"filepath": filepath, "task": task})

    async def _flush_pending(self):
        """Flush buffered tasks after (re)connection."""
        if not self.pending_tasks or not self.writer:
            return
        
        print(f"[TCP] Flushing {len(self.pending_tasks)} pending task(s)")
        remaining = []
        for item in self.pending_tasks:
            try:
                await self.send_task(item.get("filepath"), item.get("task"))
            except Exception as e:
                print("[TCP] Flush error:", e)
                remaining.append(item)
        self.pending_tasks = remaining


def start_gateway_tcp(ip: str = GW_IP, port: int = GW_TCP_PORT):
    """
    Start the GatewayClient in its own asyncio loop/thread.
    """
    ota_gw = GatewayClient(ip, port)

    def run_loop():
        loop = asyncio.new_event_loop()
        ota_gw.loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(ota_gw.run())
        finally:
            loop.close()

    threading.Thread(target=run_loop, daemon=True).start()

    # Subscribe to dispatch → trigger send_task
    def handle_tcp_send(payload):
        filepath = payload.get("filepath")
        task = payload.get("task_json")
        if filepath is None or task is None:
            print("[TCP] Invalid payload for send:", payload)
            return
        
        if ota_gw.loop is None or ota_gw.loop.is_closed():
            print("[TCP] Loop not ready; buffering task")
            ota_gw.pending_tasks.append({"filepath": filepath, "task": task})
            return
        
        asyncio.run_coroutine_threadsafe(
            ota_gw.send_task(filepath, task),
            ota_gw.loop
        )

    bus.subscribe("dispatch.task_send", handle_tcp_send)
    print("[TCP] Gateway client started")