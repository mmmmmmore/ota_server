import asyncio, json, time
import socket
import re
import threading
from routes.base_value import GW_IP, GW_TCP_PORT
from routes.messagebus import bus



class GatewayClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.ackseq = 0
        self.loop = None
        self.writer = None

    async def run(self):
        while True:
            try:
                hello_msg ={"msg_type":"hello", "role":"ota_server"}
                reader, writer = await asyncio.open_connection(self.ip, self.port)
                print("[TCP] Connected to GW")
                sock = writer.get_extra_info('socket')
                if sock is not None:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                writer.write((json.dumps(hello_msg)+'\n').encode())
                await writer.drain()
                #print("[TCP] Tx hello to OTA GW finished")

                async def sender(filepath, task):
                    if not self.writer:
                        print("[TCP] writer not ready, GW not connected")
                        return
                    payload = json.dumps(task) + "\n"
                    self.writer.write(payload.encode())
                        await writer.drain()
                        print(f"[TCP] Sent task: {repr(payload)}")
                        task["status"] = "success"    ## need change the phase and result 
                        with open(filepath, "w") as f:
                            json.dump(task, f, indent=2)
                        bus.publish("task.sent", {"filepath":filepath, "task":task})

                async def receiver():
                    while True:
                        data = await reader.readline()
                        if not data:
                            print("[TCP] GW disconnected")
                            break
                        msg = data.decode().strip()
                        try:
                            obj = json.loads(msg)
                            if obj.get("msg_type") == "keep_alive":
                                ack = {"msg_type": f"keep_alive_ack{str(self.ackseq)}"}
                                self.ackseq += 1
                                if "seq" in obj: 
                                    ack["seq"] = obj["seq"]
                                writer.write((json.dumps(ack) + "\n").encode())
                                await writer.drain()
                                print("[TCP] Sent keep_alive_ack")
                            elif obj.get("msg_type") == "ota_task_ack":
                                bus.publish("tcp.update_task", obj)
                            elif obj.get("msg_type") == "register":
                                bus.publish("tc[].device_update", obj)
                            else:
                                print("[TCP] GW message:", obj)
                        except Exception as e:
                            print("[TCP] Parse error:", e, msg)
                await asyncio.gather(sender(), receiver())
            except Exception as e:
                print("[TCP] Connection error:", e)
                await asyncio.sleep(5)


def start_gateway_tcp(ip, port, queue_size=200):
    queue = asyncio.Queue(maxsize=queue_size)
    ota_gw = GatewayClient(ip, port, queue)
    
    def run_loop():
        loop = asyncio.new_event_loop()
        ota_gw.loop = loop
        asyncio.set_event_loop(loop)
        loop.run_until_complete(ota_gw.run())
    
    tcp_thread = threading.Thread(target= run_loop, daemon= True)
    tcp_thread.start()
    
    ## subscribe the bus
    def handle_tcp_send(payload):
        filepath = payload.get("filepath")
        task = payload.get("task")
        
        fut = asyncio.run_coroutine_threadsafe(ota_gw.queue.put((filepath, task)), ota_gw.loop)
        fut.result()
        
    
    bus.subscribe("dispatch.task_send", handle_tcp_send)
    
    print("[TCP] Gateway client started")
    
    
    