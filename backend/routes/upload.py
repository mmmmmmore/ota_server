from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import json

upload_bp = Blueprint("upload", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "db")
SOFTWARE_FILE = os.path.join(DB_DIR, "software_list.json")
FIRMWARE_DIR = os.path.join(BASE_DIR, "firmware")
os.makedirs(FIRMWARE_DIR, exist_ok=True)

software_versions = []  # 引用或共享版本列表



def load_software():
    if not os.path.exists(SOFTWARE_FILE):
        return []
    with open(SOFTWARE_FILE, "r") as f:
        return json.load(f)

def save_software(data):
    with open(SOFTWARE_FILE, "w") as f:
        json.dump(data, f, indent=2)

@upload_bp.route("/api/upload", methods=["POST"])
def upload_firmware():
    file = request.files.get("file")
    version = request.form.get("version")
    md5 = request.form.get("md5")
    changes = request.form.get("changes")

    if not file or not version:
        return jsonify({"error": "缺少必要字段"}), 400

    # 保存固件文件，以版本号命名
    save_path = os.path.join(FIRMWARE_DIR, f"{file.filename}_{version}")
    file.save(save_path)

    # 更新 software_list.json
    software_list = load_software()
    new_entry = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "changes": changes,
        "md5": md5
    }
    software_list.append(new_entry)
    save_software(software_list)

    return jsonify({"message": "上传成功", "version": version, "md5": md5}), 201
