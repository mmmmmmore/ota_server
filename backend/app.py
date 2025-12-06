from flask import Flask
from flask_cors import CORS
import asyncio, threading



# 导入蓝图
from routes.devices import devices_bp
from routes.software import software_bp
from routes.upload import upload_bp
from routes.dispatch import dispatch_bp, task_queue, loop
from routes.download import download_bp
from routes.tcp_async import GatewayClient

GW_IP = "192.168.4.1"
GW_TCP_PORT = 9001

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}},supports_credentials=True)  # 解决跨域问题，前端不同源也能访问 # config the cert



# 注册蓝图
app.register_blueprint(devices_bp)
app.register_blueprint(software_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(dispatch_bp)
app.register_blueprint(download_bp)



def start_asyncio():
    global loop, task_queue
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task_queue = asyncio.Queue()
    client = GatewayClient(GW_IP, GW_TCP_PORT, task_queue)
    loop.run_until_complete(client.run())

threading.Thread(target= start_asyncio, daemon=True ).start()

if __name__ == "__main__":
    context = ("server.crt","server.key")
    app.run(host="0.0.0.0", port=8080, debug=True,  ssl_context = context)

