import asyncio, json, time

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
                #hello_payload = json.dumps(hellp_msg) +'\n'
                writer.write((json.dumps(hellp_msg)+'\n').encode())
                await writer.drain()
                print("[TCP] Tx hello to OTA GW finished")

                async def sender():
                    while True:
                        filepath, task = await self.queue.get()
                        payload = json.dumps(task) + "\n"
                        writer.write(payload.encode())
                        await writer.drain()
                        print(f"[TCP] Sent task: {payload.strip()}")
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
                            else:
                                print("[TCP] GW message:", obj)
                        except Exception as e:
                            print("[TCP] Parse error:", e, msg)

                await asyncio.gather(sender(), receiver())
            except Exception as e:
                print("[TCP] Connection error:", e)
                await asyncio.sleep(5)

