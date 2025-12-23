from flask import Flask
from flask_cors import CORS
import asyncio, threading
from fastapi.staticfiles import StaticFiles
from routes.task import STATIC_DIR
import ssl
import eventlet
from routes.base_value import SERVERCRT
from routes.base_value import SERVERKEY

# 导入蓝图
from routes.devices import devices_bp
from routes.software import software_bp
from routes.upload import upload_bp
from routes.dispatch import dispatch_bp, tcpthread
from routes.download import download_bp
from routes.websock import socketio


app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app, resources={r"/*":{"origins":"*"}},supports_credentials=True)  # 解决跨域问题，前端不同源也能访问 # config the cert


# 注册蓝图
app.register_blueprint(devices_bp)
app.register_blueprint(software_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(dispatch_bp)
app.register_blueprint(download_bp)





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
                 debug=False,
                 use_reloader=False,
                 ssl_context = context
    #             allow_unsafe_werkzeug=True
                )
