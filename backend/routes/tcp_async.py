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
        # connection retry/backoff settings
        self.retry_delay = 1  # initial retry delay in seconds (exponential backoff)
        self.max_retry_delay = 60  # maximum retry delay in seconds
        # keepalive policy: if we received a keepalive within this window, avoid reconnecting
        self.keepalive_timeout = 30  # seconds (tunable)

    async def run(self):
        """Main connection loop with auto-reconnect, improved stability, and backoff.

        Strategy change: if a recent keepalive has been received (within `keepalive_timeout`),
        we delay reconnect attempts until the keepalive expires instead of immediate reconnects.
        """
        while True:
            # Bump connection id to represent a new connection attempt
            self._connection_id += 1
            connection_id = self._connection_id
            print(f"[Backend-TCP] Connection attempt #{connection_id}, connected={self.connected}, retry_delay={self.retry_delay}s")

            # default sleep_time is current retry_delay; may be overridden below
            sleep_time = self.retry_delay

            # If we've recently received a keepalive, skip initiating a new connection
            # until the keepalive window expires. This ensures we do not reconnect while
            # the GW is actively sending keepalives.
            elapsed_since_ack = time.time() - self.last_ack if self.last_ack else float('inf')
            if elapsed_since_ack < self.keepalive_timeout:
                delay = max(1, int(self.keepalive_timeout - elapsed_since_ack))
                print(f"[TCP_Async] Recent keepalive ({elapsed_since_ack:.1f}s ago); skipping connect for {delay}s (#{connection_id})")
                await asyncio.sleep(delay)
                continue

            try:
                # Check if already connected
                async with self.conn_lock:
                    if self.connected and self.writer and not self.writer.is_closing():
                        print(f"[Backend-TCP] Already connected (#{connection_id}), skipping")
                        await asyncio.sleep(self.retry_delay)
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
                    # mark which connection this writer belongs to (used during cleanup)
                    try:
                        setattr(self.writer, "_connection_id", connection_id)
                    except Exception:
                        pass
                    self.connected = True
                    self.last_ack = time.time()

                    print(f"[TCP_Async] Connected with GW (#{connection_id})")

                    # Send hello handshake
                    hello_msg = {"msg_type": "hello", "role": "ota_server"}
                    writer.write((json.dumps(hello_msg) + "\n").encode())
                    await writer.drain()

                    # Flush any pending tasks
                    await self._flush_pending()

                # Start receiver as a task (so it can be cancelled from elsewhere)
                self._receiver_task = asyncio.create_task(self.receiver(reader, writer, connection_id))

                # Wait for receiver to finish; if it raises, we'll handle in except
                await self._receiver_task

                # If receiver exited without exception, reset retry backoff
                self.retry_delay = 1
                sleep_time = self.retry_delay

            except asyncio.CancelledError:
                print(f"[TCP_Async] Connection task cancelled (#{connection_id})")
                break
            except Exception as e:
                print(f"[TCP_Async] Connection error (#{connection_id}): {e}")
                # If a recent keepalive was received, delay reconnecting until it becomes stale
                elapsed = time.time() - self.last_ack if self.last_ack else float("inf")
                if elapsed < self.keepalive_timeout:
                    # Wait until the keepalive window expires before retrying
                    sleep_time = max(1, int(self.keepalive_timeout - elapsed))
                    print(f"[TCP_Async] Recent keepalive ({elapsed:.1f}s ago); delaying reconnect for {sleep_time}s (#{connection_id})")
                    # do not update retry_delay (keep it where it was)
                else:
                    # exponential backoff on repeated failures
                    self.retry_delay = min(self.max_retry_delay, max(1, self.retry_delay * 2))
                    sleep_time = self.retry_delay
                    print(f"[TCP_Async] Next retry after {self.retry_delay}s (#{connection_id})")

            finally:
                # Cleanup: only close resources that belong to this connection id
                async with self.conn_lock:
                    if getattr(self.writer, "_connection_id", None) == connection_id:
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

                print(f"[TCP_Async] Disconnected from GW (#{connection_id}), retry in {sleep_time}s")
                await asyncio.sleep(sleep_time)

    async def receiver(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, connection_id: int):
        """Receive messages from GW and publish to MessageBus.

        Note: on EOF or unexpected errors we raise so `run()` applies backoff.
        """
        try:
            print(f"[TCP_Async] Receiver started (#{connection_id})")
            while True:
                data = await reader.readline()
                if not data:
                    # Treat EOF as connection loss and raise to propagate to run()
                    raise ConnectionError(f"GW disconnected (#{connection_id})")

                msg = data.decode(errors="replace").strip()
                if not msg:
                    continue

                obj = None
                try:
                    obj = json.loads(msg)
                except Exception as e:
                    # Attempt to extract JSON substring from noisy lines (e.g. "CLIENT_REGISTER: ... {json}")
                    start = msg.find("{")
                    end = msg.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        json_part = msg[start:end+1]
                        try:
                            obj = json.loads(json_part)
                            print(f"[TCP] Extracted JSON from noisy message (#{connection_id}):", json_part)
                        except Exception as e2:
                            print(f"[TCP] Parse error after extraction (#{connection_id}):", e2, msg)
                            continue
                    else:
                        print(f"[TCP] Parse error (#{connection_id}):", e, msg)
                        continue

                # Dispatch by msg_type
                mt = obj.get("msg_type") if isinstance(obj, dict) else None
                if mt == "keep_alive":
                    # Use the local writer parameter, not self.writer
                    await self._send_keepalive_ack(writer, obj, connection_id)
                    self.last_ack = time.time()
                    print(f'[TCP] Keepalive received (#{connection_id})')

                elif mt == "ota_task_ack":
                    bus.publish("tcp.update_task", obj)
                    print(f"[TCP_Async] Rx task_ack from GW (#{connection_id})", obj)

                elif mt == "register":
                    client_id = obj.get("client_id")
                    version = obj.get("version")
                    print(obj)
                    print(f"[TCP_Async] Rx register from GW (#{connection_id}) client_id={client_id} version={version}")
                    bus.publish("tcp.device_update", obj)
                    print(f"[Backend-TCP] Device registered (#{connection_id}) client_id={client_id}")
                else:
                    print(f"[TCP] GW message (#{connection_id}):", obj)

        except asyncio.CancelledError:
            print(f"[TCP_Async] Receiver cancelled (#{connection_id})")
            raise
        except Exception as e:
            # Log and re-raise so run() will backoff
            print(f"[TCP_Async] Receiver error (#{connection_id}):", e)
            raise
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