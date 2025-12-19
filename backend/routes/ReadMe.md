from flask import Flask
import asyncio, threading
from dispatch import dispatch_bp, task_queue
from tcp_async import GatewayClient

app = Flask(__name__)
app.register_blueprint(dispatch_bp)

def start_asyncio():
    global loop, task_queue
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task_queue = asyncio.Queue()
    client = GatewayClient("192.168.4.1", 9001, task_queue)
    loop.run_until_complete(client.run())

threading.Thread(target=start_asyncio, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
