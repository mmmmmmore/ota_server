# dispatch.py
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
import netifaces
from tcpconnect import get_socket   # 引用新的模块

dispatch_bp = Blueprint("dispatch", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)

def create_task_file(device_name, client_id, version):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_id = f"{timestamp}_{client_id}"
    filename = f"{task_id}.json"
    filepath = os.path.join(TASK_DIR, filename)

    current_ip = netifaces.ifaddresses("en0")[netifaces.AF_INET][0]['addr']
    task = {
        "msg_type":"ota_task",
        "task_id": task_id,
        "device_name": device_name,
        "client_id": client_id,
        "version": version,
        "firmware_url": f"https://{current_ip}:8080/firmware/firmware_{version}.bin",
        "timestamp": timestamp,
        "status": "pending"
    }

    with open(filepath, "w") as f:
        json.dump(task, f, indent=2)

    return filepath, task

def update_task_status(filepath, task, status, error=None):
    task["status"] = status
    if error:
        task["error"] = error
    with open(filepath, "w") as f:
        json.dump(task, f, indent=2)

@dispatch_bp.route("/api/dispatch/push", methods=["POST"])
def push_task():
    data = request.get_json()
    device_name = data.get("device_name")
    client_id = data.get("client_id")
    version = data.get("version")

    filepath, task = create_task_file(device_name, client_id, version)

    gw_sock = get_socket()
    if gw_sock is None:
        update_task_status(filepath, task, "failed", "GW not connected")
        return jsonify({"error": "GW not connected"}), 503

    try:
        gw_sock.sendall(json.dumps(task).encode("utf-8"))
        update_task_status(filepath, task, "success")
        return jsonify({"message": "OTA Push Success", "task": task}), 200
    except Exception as e:
        update_task_status(filepath, task, "failed", str(e))
        return jsonify({"error": f"Push Err: {str(e)}"}), 500
