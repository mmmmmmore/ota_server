import os
import json
import socket
from datetime import datetime
from flask import Blueprint, request, jsonify

dispatch_bp = Blueprint("dispatch", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)

GW_IP = "192.168.4.1"
GW_PORT = 9000  # 假设网关监听端口9000


def create_task_file(device_name, client_id, version):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{device_name}_{client_id}.json"
    filepath = os.path.join(TASK_DIR, filename)
    
    task = {
        "device_name": device_name,
        "client_id": client_id,
        "version": version,
        "timestamp": timestamp,
        "status": "pending"
    }
    
    with open(filepath, "w") as f:
        json.dump(task, f, indent=2)
    
    return filepath, task


def is_gateway_online():
    try:
        sock = socket.create_connection((GW_IP, GW_PORT), timeout=3)
        sock.close()
        return True
    except Exception:
        return False





@dispatch_bp.route("/api/dispatch/push", methods=["POST"])
def push_task():
    data = request.get_json()
    device_name = data.get("device_name")
    client_id = data.get("client_id")
    version = data.get("version")

    if not device_name or not client_id or not version:
        return jsonify({"error": "缺少必要字段"}), 400

    filepath, task = create_task_file(device_name, client_id, version)

    # 检查网关是否在线
    if not is_gateway_online():
        update_task_status(filepath, task, "failed", "Network not connect to GW, please retry connection... ")
        return jsonify({"error", "Network Connection Err"}), 503

    # 推送任务到网关
    try:
        sock = socket.create_connection((GW_IP, GW_PORT), timeout=5)
        sock.sendall(json.dumps(task).encode("utf-8"))
        sock.close()
        update_task_status(filepath, task, "success")
        return jsonify({"message": "OTA Push Success ", "task": task}), 200
    except Exception as e:
        update_task_status(filepath, task, "failed", str(e))
        return jsonify({"error": f"Push Err: {str(e)}"}), 500



def update_task_status(filepath, task, status, error=None):
    task["status"] = status
    if error:
        task["error"] =error
    with open(filepath, "w") as f:

        json.dump(task, f, indent=2)
