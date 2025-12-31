# backend/tcp_async.py
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
    TCP client to OTA_GW:
    - Preserves TCP_NODELAY for low-latency sending
    - Receiving path continuously reads from GW and publishes to MessageBus
    - Sending path is triggered by MessageBus subscription (no internal asyncio.Queue)
    """
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.ackseq: int = 0
        # Optional buffering: tasks queued when GW not connected
        self.pending_tasks: List[Dict[str, Any]] = []
        self.connected: bool = False  # OTA server connection with GW 
        self.lask_ack =0
        self.conn_lock = asyncio.Lock()
        self.last_keepalive_ack =0
        self.keepalive_ack_interval=5  # seconds
        

    async def run(self):
        """Main connection loop with auto-reconnect and TCP_NODELAY."""
        while True:
            try:
                
                reader, writer = await asyncio.open_connection(self.ip, self.port)
                
                sock = writer.get_extra_info("socket")
                if sock :
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                
                # Check if we already have a healthy connection
                async with self.conn_lock:
                    self.writer = writer
                    self.connected = True
                    self.lask_ack = time.time()
                    print("[TCP_Async] Connected with GW")
                    
                    # Hello handshake
                    hello_msg = {"msg_type": "hello", "role": "ota_server"}
                    writer.write((json.dumps(hello_msg) + "\n").encode())
                    await writer.drain()
                    
                    await self._flush_pending()
                    
                    await self.receiver(reader, writer)
                    
            except Exception as e:
                print(f"[TCP_Async] Connection error: {e}")
            
            finally:
                
                async with self.conn_lock:
                    self.connected= False
                    if self.writer:
                        try:
                            self.writer.close()
                            await self.writer.wait_closed()
                        except Exception:
                            pass
                        self.writer =None
                print("[TCP_Async] Disconnected with GW, retry in 10s")
                await asyncio.sleep(10)
                    

    
    async def receiver(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Receive messages from GW and publish to MessageBus."""
        try:
            while True:
                data = await reader.readline()
                if not data:
                    print("[TCP] GW disconnected")
                    break

                msg = data.decode(errors="replace").strip()
                if not msg:
                    continue

                try:
                    obj = json.loads(msg)
                except Exception as e:
                    print("[TCP] Parse error:", e, msg)
                    continue

                # Dispatch by msg_type
                mt = obj.get("msg_type")
                if mt == "keep_alive":
                    await self._send_keepalive_ack(writer, obj)
                    self.lask_ack = time.time()
                    
                    self.connected = True
                elif mt == "ota_task_ack":
                    bus.publish("tcp.update_task", obj)
                    print("[TCP_Async] Rx task_ack from GW", obj)
                elif mt == "register":
                    bus.publish("tcp.device_update", obj)
                    print(f"[Backend-TCP] device new register online, need update the result")
                else:
                    print("[TCP] GW message:", obj)
        except asyncio.CancelledError:
            print("[TCP_Async] Receiver canncelled")
        
        except Exception as e:
            print("[TCP_Async] Received error: ", e)
        
        finally:
            print("[TCP_Async] Receiver exiting")
            

    async def _send_keepalive_ack(self, writer: asyncio.StreamWriter, obj: Dict[str, Any]):
        if not self.writer:
            return
        
        now = time.time()
        if now- self.last_keepalive_ack < self.keepalive_ack_interval:
            return
        
        
        """Reply to keep_alive with ack."""
        ack = {"msg_type": f"keep_alive_ack"}
        try:
            self.writer.write((json.dumps(ack)+'\n').encode())
            await self.writer.drain()
            self.last_keepalive_ack =now
            print("[TCP_Async] Tx keepalive_ack ")
        except Exception as e:
            print("[TCP_Async] keepalive sent failed: ",e)
            
            

    async def send_task(self, filepath: str, task: Dict[str, Any]):
        """
        Send a task to GW. If not connected, buffer for later flush.
        Triggered by MessageBus subscription (no internal queue).
        """
        if not task or not isinstance(task, dict):
            print("[TCP] Invalid task payload:", task)
            return

        # If GW not connected, buffer
        if not self.writer:
            print("[TCP] GW not connected; buffering task")
            self.pending_tasks.append({"filepath": filepath, "task": task})
            return

        payload_str = json.dumps(task) + "\n"
        try:
            self.writer.write(payload_str.encode())
            await self.writer.drain()
            print(f"[TCP] Sent task: {payload_str!r}")
        except Exception as e:
            print("[TCP] Send error, buffering task:", e)
            self.pending_tasks.append({"filepath": filepath, "task": task})
            return

        # Update status and publish sent event
        try:
            task["status"] = "success"  # TODO: refine with proper states
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
    Start the GatewayClient in its own asyncio loop/thread and subscribe to dispatch.
    Sending is messageBus-driven; receiving publishes back to bus.
    """
    ota_gw = GatewayClient(ip, port)

    def run_loop():
        loop = asyncio.new_event_loop()
        ota_gw.loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ota_gw.run())

    threading.Thread(target=run_loop, daemon=True).start()

    # Subscribe to dispatch → trigger send_task
    def handle_tcp_send(payload):
        filepath = payload.get("filepath")
        task = payload.get("task_json")
        if filepath is None or task is None:
            print("[TCP] invalid payload for send:", payload)
            return
        if ota_gw.loop is None:
            print("[TCP] loop not ready; buffering task")
            ota_gw.pending_tasks.append({"filepath": filepath, "task": task})
            return
        asyncio.run_coroutine_threadsafe(
            ota_gw.send_task(filepath, task),
            ota_gw.loop
        )

    bus.subscribe("dispatch.task_send", handle_tcp_send)
    print("[TCP] Gateway client started")
