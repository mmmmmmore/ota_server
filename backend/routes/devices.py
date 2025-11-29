import json
import os
from flask import Blueprint, jsonify, request


devices_bp = Blueprint("devices", __name__)

## JSON save path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR,'..','db')
DEVICES_FILE = os.path.join(DB_DIR, "devices.json")


## initiate check
if not os.path.exists(DEVICES_FILE):
    with open(DEVICES_FILE, "w") as f:
        json.dump([],f)
        

def load_devices():
    with open(DEVICES_FILE, 'r') as f:
        return json.load(f)
    

def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)




# 模拟设备存储（后续可以替换成数据库或文件）
#devices = [
#    {"name": "Vehicle_1", "ip": "192.168.4.2", "version": "v1.0.0", "partition": "A", "status": "online"},
#    {"name": "Vehicle_2", "ip": "192.168.4.3", "version": "v1.0.0", "partition": "A", "status": "online"},
#    {"name": "Vehicle_3", "ip": "192.168.4.4", "version": "v1.0.0", "partition": "A", "status": "offline"},
#]

# 查询设备列表
@devices_bp.route("/api/devices", methods=["GET"])
def get_devices():
    devices = load_devices()
    return jsonify(devices)

# 新建设备
@devices_bp.route("/api/devices/register", methods=["POST"])
def register_device():
    data = request.get_json()
    print("Rx Json: ",data)
    if not data or "device_name" not in data or "mac_address" not in data :
        return jsonify({"error": "缺少必要字段"}), 400

    devices = load_devices()
    
    # 检查是否已存在同名或同IP设备
    for d in devices:
        if d["mac_address"] == data["mac_address"] :
            return jsonify({"error": "设备已存在"}), 409

    # 构造新设备
    new_device = {
        "device_name": data["device_name"],
        "mac_address": data["mac_address"],
        "client_id": data.get("client_id"),
        "ip": None,
        "version": data.get("version", "unknown"),
        "partition": None,
        "status": None
    }
    devices.append(new_device)
    save_devices(devices)

    return jsonify(new_device), 201
