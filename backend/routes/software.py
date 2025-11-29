import os
import json
from flask import Blueprint, request, jsonify
from datetime import datetime

software_bp = Blueprint("software", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "db")
SOFTWARE_FILE = os.path.join(DB_DIR, "software_list.json")
FIRMWARE_DIR = os.path.join(DB_DIR, "firmware")

# 确保目录存在
os.makedirs(FIRMWARE_DIR, exist_ok=True)

# 初始化 JSON 文件为空数组
if not os.path.exists(SOFTWARE_FILE):
    with open(SOFTWARE_FILE, "w") as f:
        json.dump([], f)

def load_software():
    with open(SOFTWARE_FILE, "r") as f:
        return json.load(f)

def save_software(data):
    with open(SOFTWARE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 查询所有软件版本
@software_bp.route("/api/software", methods=["GET"])
def get_software():
    return jsonify(load_software())

# 上传新固件（增）
@software_bp.route("/api/software/upload", methods=["POST"])
def upload_software():
    file = request.files.get("file")
    version = request.form.get("version")
    md5 = request.form.get("md5")
    changes = request.form.get("changes")

    if not file or not version:
        return jsonify({"error": "缺少必要字段"}), 400

    # 保存固件文件，以版本号命名
    save_path = os.path.join(FIRMWARE_DIR, f"{version}_{file.filename}")
    file.save(save_path)

    # 更新 JSON 列表
    software_list = load_software()
    # 检查是否已存在版本
    for s in software_list:
        if s["version"] == version:
            return jsonify({"error": "版本已存在"}), 409

    new_entry = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "changes": changes or "",
        "md5": md5 or "",
        "filename": f"{version}_{file.filename}"  # 记录固件文件名
    }
    software_list.append(new_entry)
    save_software(software_list)

    return jsonify(new_entry), 201

# 修改软件版本信息（改）
@software_bp.route("/api/software/<version>", methods=["PUT"])
def update_software(version):
    data = request.get_json()
    software_list = load_software()

    for s in software_list:
        if s["version"] == version:
            s["release_date"] = data.get("release_date", s["release_date"])
            s["changes"] = data.get("changes", s["changes"])
            s["md5"] = data.get("md5", s["md5"])
            save_software(software_list)
            return jsonify(s), 200

    return jsonify({"error": "版本未找到"}), 404

# 删除软件版本（删）
@software_bp.route("/api/software/<version>", methods=["DELETE"])
def delete_software(version):
    software_list = load_software()
    new_list = []
    deleted_entry = None

    for s in software_list:
        if s["version"] == version:
            deleted_entry = s
        else:
            new_list.append(s)

    if not deleted_entry:
        return jsonify({"error": "版本未找到"}), 404

    # 删除对应固件文件
    firmware_path = os.path.join(FIRMWARE_DIR, deleted_entry.get("filename", ""))
    if os.path.exists(firmware_path):
        os.remove(firmware_path)

    save_software(new_list)
    return jsonify({"message": f"版本 {version} 已删除"}), 200
