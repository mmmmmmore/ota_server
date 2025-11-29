from flask import Blueprint, jsonify, request

devices_bp = Blueprint("devices", __name__)

# 模拟设备存储（后续可以替换成数据库或文件）
devices = [
    {"name": "Vehicle_1", "ip": "192.168.4.2", "version": "v1.0.0", "partition": "A", "status": "online"},
    {"name": "Vehicle_2", "ip": "192.168.4.3", "version": "v1.0.0", "partition": "A", "status": "online"},
    {"name": "Vehicle_3", "ip": "192.168.4.4", "version": "v1.0.0", "partition": "A", "status": "offline"},
]

# 查询设备列表
@devices_bp.route("/api/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

# 新建设备
@devices_bp.route("/api/devices/register", methods=["POST"])
def register_device():
    data = request.get_json()
    if not data or "name" not in data or "ip" not in data:
        return jsonify({"error": "缺少必要字段"}), 400

    # 检查是否已存在同名或同IP设备
    for d in devices:
        if d["name"] == data["name"] or d["ip"] == data["ip"]:
            return jsonify({"error": "设备已存在"}), 409

    # 构造新设备
    new_device = {
        "name": data["name"],
        "ip": data["ip"],
        "version": data.get("version", "unknown"),
        "partition": data.get("partition", "A"),
        "status": data.get("status", "offline")
    }
    devices.append(new_device)

    return jsonify(new_device), 201
