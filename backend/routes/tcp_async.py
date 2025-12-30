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
        

    async def run(self):
        """Main connection loop with auto-reconnect and TCP_NODELAY."""
        while True:
            try:
                async with self.conn_lock:
                    
                    if self.writer :
                        print("..............write alive")
                        if time.time() - self.lask_ack < 30:
                            print(f"[Backend-TCP]{time.time()-self.lask_ack}")
                            await asyncio.sleep(5)
                            continue
                    reader, writer = await asyncio.open_connection(self.ip, self.port)
                    self.writer = writer
                    self.connected = True
                    print("[TCP] Connected to GW")

                # Set TCP_NODELAY
                    sock = writer.get_extra_info('socket')
                    if sock is not None:
                        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                # Hello handshake
                    hello_msg = {"msg_type": "hello", "role": "ota_server"}
                    writer.write((json.dumps(hello_msg) + "\n").encode())
                    await writer.drain()

                # Flush any pending tasks (if any)
                    await self._flush_pending()

                # Start receiver loop (blocking until disconnect)
                    await self.receiver(reader, writer)

            except Exception as e:
                print("[TCP] Connection error:", e)
            finally:
                # Cleanup on disconnect
                try:
                    if self.writer:
                        self.writer.close()
                        # In asyncio 3.11+, can await writer.wait_closed()
                except Exception:
                    pass
                self.writer = None

            # Backoff before reconnect
            await asyncio.sleep(5)

    async def receiver(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Receive messages from GW and publish to MessageBus."""
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
            elif mt == "register":
                bus.publish("tcp.device_update", obj)
            else:
                print("[TCP] GW message:", obj)
            
        # after all connection finished
        self.connected = False

    async def _send_keepalive_ack(self, writer: asyncio.StreamWriter, obj: Dict[str, Any]):
        """Reply to keep_alive with ack."""
        ack = {"msg_type": f"keep_alive_ack"}
        writer.write((json.dumps(ack) + "\n").encode())
        await writer.drain()
        print("[TCP] Sent keep_alive_ack")

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
