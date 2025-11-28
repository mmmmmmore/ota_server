from flask import Blueprint, request, jsonify
import os
from datetime import datetime

upload_bp = Blueprint("upload", __name__)
FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), "../firmware")
os.makedirs(FIRMWARE_DIR, exist_ok=True)

software_versions = []  # 引用或共享版本列表

@upload_bp.route("/api/upload", methods=["POST"])
def upload_firmware():
    file = request.files.get("file")
    version = request.form.get("version", "unknown")
    if file:
        # 改进：按版本号命名文件，避免覆盖
        filename = f"firmware_{version}.bin"
        filepath = os.path.join(FIRMWARE_DIR, filename)
        file.save(filepath)

        software_versions.append({
            "version": version,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hardware": request.form.get("hardware", "HW_Ax"),
            "changes": request.form.get("changes", "新上传版本"),
            "file": filename
        })
        return jsonify({"status": "ok", "version": version})
    return jsonify({"status": "fail"}), 400
