import asyncio, json, time
import socket
import re
from routes.devices import update_device_partition
from routes.devices import update_device_connection
from routes.websock import socketio


class GatewayClient:
    def __init__(self, ip, port, queue):
        self.ip = ip
        self.port = port
        self.queue = queue
        self.ackseq = 0

    async def run(self):
        while True:
            try:
                
                hellp_msg ={"msg_type":"hello", "role":"ota_server"}
                reader, writer = await asyncio.open_connection(self.ip, self.port)
                print("[TCP] Connected to GW")
                sock = writer.get_extra_info('socket')
                if sock is not None:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                hello_payload = json.dumps(hellp_msg) +'\n'
                writer.write((json.dumps(hellp_msg)+'\n').encode())
                await writer.drain()
                #print("[TCP] Tx hello to OTA GW finished")

                async def sender():
                    while True:
                        filepath, task = await self.queue.get()
                        payload = json.dumps(task) + "\n"
                        writer.write(payload.encode())
                        await writer.drain()
                        print(f"[TCP] Sent task: {repr(payload)}")
                        task["status"] = "success"
                        with open(filepath, "w") as f:
                            json.dump(task, f, indent=2)

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
                                ota_task_id = obj.get("task_id")
                                ota_task_client_id = re.split("_",ota_task_id)[-1]  ## split the client id
                                ota_task_status = obj.get("status")  ## parse the result
                                update_device_partition(ota_task_client_id,ota_task_status)  # update the partition after ack
                                
                                push_msg_2_front(obj)  # push ota task json to front
                            elif obj.get("msg_type") == "register":
                                ota_client_id = obj.get("client_id")
                                ota_client_connect_state = obj.get("connect_state")
                                update_device_connection(ota_client_id,ota_client_connect_state)
                                push_msg_2_front(obj)
                            else:
                                print("[TCP] GW message:", obj)
                        except Exception as e:
                            print("[TCP] Parse error:", e, msg)

                await asyncio.gather(sender(), receiver())
            except Exception as e:
                print("[TCP] Connection error:", e)
                await asyncio.sleep(5)

    async def push_msg_2_front(payload: dict):  ## json format
        socketio.emit("ota_task_update",payload)
        print(f"[WebSocket] pushed ota task update info to front")