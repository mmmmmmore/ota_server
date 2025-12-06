import asyncio, json, time

class GatewayClient:
    def __init__(self, ip, port, queue):
        self.ip = ip
        self.port = port
        self.queue = queue

    async def run(self):
        while True:
            try:
                reader, writer = await asyncio.open_connection(self.ip, self.port)
                print("[TCP] Connected to GW")

                async def sender():
                    while True:
                        task = await self.queue.get()
                        payload = json.dumps(task) + "\n"
                        writer.write(payload.encode())
                        await writer.drain()
                        print(f"[TCP] Sent task: {payload.strip()}")

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
                                ack = {"msg_type": "keep_alive_ack"}
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
