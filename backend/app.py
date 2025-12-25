from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO


import ssl
import eventlet
from routes.base_value import SERVERCRT, SERVERKEY, GW_IP, GW_TCP_PORT

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


app = Flask(__name__)
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

if __name__ == "__main__":
    tcpthread.start()

    #context = ("server.crt", "server.key")
    #app.run(host="0.0.0.0", port=8080, debug=True,  ssl_context = context)
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=SERVERCRT,keyfile=SERVERKEY)
    
    socketio.init_app(app, cors_allowed_origins= "*")
    #eventlet.wsgi.server(
    #    eventlet.listen(("0.0.0.0", 8080)),
    #    app,
    #    ssl_args={"certfile":SERVERCRT, "keyfile":SERVERKEY}
    #)
    #socketio.run(app,host="0.0.0.0", port=8080, debug=True,  ssl_context = ("server.crt", "server.key"))
    
    socketio.run(app, host="0.0.0.0", 
                 port=8080, 
                 certfile = SERVERCRT,
                 keyfile = SERVERKEY
    #             debug=False,
    #             use_reloader=False,
    #             ssl_context = context
    #             allow_unsafe_werkzeug=True
                )
