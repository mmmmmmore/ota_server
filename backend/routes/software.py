from flask import Blueprint, jsonify, request
import os,json



software_bp = Blueprint("software", __name__)


## JSON save path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR,'..','db')
SOFTWARE_FILE = os.path.join(DB_DIR, "software_list.json")


## initiate check
if not os.path.exists(SOFTWARE_FILE):
    with open(SOFTWARE_FILE, "w") as f:
        json.dump([],f)
        

def load_softwares():
    with open(SOFTWARE_FILE, 'r') as f:
        return json.load(f)
    

def save_softwares(data):
    with open(SOFTWARE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


## resolve the firmware package






#software_versions = [
#    {"version": "v1.0.0", "date": "2025-11-01", "hardware": "HW_A1", "changes": "初始版本"},
#    {"version": "v1.0.1", "date": "2025-11-05", "hardware": "HW_A1", "changes": "修复网络连接问题"},
#]

@software_bp.route("/api/software", methods=["GET"])
def get_software():
    return jsonify(load_softwares())







@software_bp.route("/api/software/upload", methods=["POST"])
def upload_software():
    data = request.get_json()
    if not data or "version" not in data or "release_date" not in data:
        return jsonify({"error": "缺少必要字段"}), 400

    software_list = load_softwares()

    # 检查是否已存在版本
    for s in software_list:
        if s["version"] == data["version"]:
            return jsonify({"error": "版本已存在"}), 409

    new_entry = {
        "version": data["version"],
        "release_date": data["release_date"],
        "changes": data.get("changes", ""),
        "md5": data.get("md5", "")
    }

    software_list.append(new_entry)
    save_softwares(software_list)

    return jsonify(new_entry), 201




@software_bp.route("/api/software/<version>", methods=["PUT"])
def update_software(version):
    data = request.get_json()
    software_list = load_softwares()

    for s in software_list:
        if s["version"] == version:
            s["release_date"] = data.get("release_date", s["release_date"])
            s["changes"] = data.get("changes", s["changes"])
            s["md5"] = data.get("md5", s["md5"])
            save_softwares(software_list)
            return jsonify(s), 200

    return jsonify({"error": "版本未找到"}), 404






@software_bp.route("/api/software/<version>", methods=["DELETE"])
def delete_software(version):
    software_list = load_softwares()
    new_list = [s for s in software_list if s["version"] != version]

    if len(new_list) == len(software_list):
        return jsonify({"error": "版本未找到"}), 404

    save_softwares(new_list)
    return jsonify({"message": f"版本 {version} 已删除"}), 200
















