from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO


import ssl
from routes.base_value import SERVERCRT, SERVERKEY, GW_IP, GW_TCP_PORT, FRONT_PATH, SERVERPEM, SERVERFULCHAIN

# 导入蓝图
from routes.devices import devices_bp
from routes.software import software_bp
from routes.upload import upload_bp
from routes.dispatch import dispatch_bp
from routes.download import download_bp
from routes.websock import socketio
from routes.tcp_async import start_gateway_tcp

from routes.devices import init_device_subscription
from routes.software import init_software_subscription
from routes.dispatch import init_dispatch_subscription
from routes.websock import init_websock_subscription


app = Flask(__name__, static_folder="front", static_url_path="")
CORS(app, resources={r"/*":{"origins":"*"}},supports_credentials=True)  # 解决跨域问题，前端不同源也能访问 # config the cert


# 注册蓝图
app.register_blueprint(devices_bp)
app.register_blueprint(software_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(dispatch_bp)
app.register_blueprint(download_bp)

start_gateway_tcp(GW_IP, GW_TCP_PORT)

init_websock_subscription()
init_device_subscription()
init_dispatch_subscription()
init_software_subscription()

@app.route("/")
def index():
    return "Hello from Flask_SocketIO"

@app.route("/index.html")
def index_html():
    return send_from_directory(FRONT_PATH, 'index.html')


@app.route("/front/<path:filename>")
def serv_front(filename):
    return send_from_directory(FRONT_PATH, filename)


socketio.init_app(app, async_mode="threading",cors_allowed_origins="*")

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    context.load_cert_chain(certfile=SERVERFULCHAIN,keyfile=SERVERKEY)
    context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384")

    
    # Werkzeug now enforces production safety; allow for local dev
    socketio.run(app, host="127.0.0.1", port=8000, debug=True, allow_unsafe_werkzeug=True)
    
    #listener = eventlet.listen(('127.0.0.1', 8080))
    #ssl_listener = eventlet.wrap_ssl(
    #    listener,
    #    ssl_context= context,
    #    server_side = True
    #)
    #eventlet.wsgi.server(ssl_listener, app)
   # socketio.init_app(app, cors_allowed_origins= "*")
   # socketio.run(app, host="0.0.0.0", 
   #              port=8080, 
   #              ssl_context = context
   #             )

