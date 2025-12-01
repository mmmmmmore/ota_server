from flask import Flask
from flask_cors import CORS

# 导入蓝图
from routes.devices import devices_bp
from routes.software import software_bp
from routes.upload import upload_bp
from routes.dispatch import dispatch_bp
from routes.download import download_bp

app = Flask(__name__)
CORS(app)  # 解决跨域问题，前端不同源也能访问

# 注册蓝图
app.register_blueprint(devices_bp)
app.register_blueprint(software_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(dispatch_bp)
app.register_blueprint(download_bp)

if __name__ == "__main__":
    context = ("server_cert.pem","server_key.pem")
    app.run(host="0.0.0.0", port=8080, debug=True,  ssl_context = context)
