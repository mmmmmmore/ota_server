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
GW_PORT = 9001  # 假设网关监听端口9000
OTA_Ser_IP = "192.168.4.2"  # server IP

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接一个外部地址，不会真的发包，只是用来获取本机 IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def create_task_file(device_name, client_id, version):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_id = f"{timestamp}_{client_id}"
    filename = f"{task_id}.json"
    filepath = os.path.join(TASK_DIR, filename)

    # 每次任务生成时动态获取当前 IP
    current_ip = get_local_ip()

    task = {
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

    filepath, task = create_task_file(device_name, client_id, version)

    if not is_gateway_online():
        update_task_status(filepath, task, "failed", "GW not reachable")
        return jsonify({"error": "Network Connection Err"}), 503

    try:
        sock = socket.create_connection((GW_IP, GW_PORT), timeout=5)
        sock.sendall(json.dumps(task).encode("utf-8"))
        response = sock.recv(1024).decode("utf-8")
        print("GW response : ", response)
        sock.close()
        update_task_status(filepath, task, "success", response)
        return jsonify({"message": "OTA Push Success", "task": task, "gw_response": response}), 200
    except Exception as e:
        update_task_status(filepath, task, "failed", str(e))
        return jsonify({"error": f"Push Err: {str(e)}"}), 500




def update_task_status(filepath, task, status, error=None):
    task["status"] = status
    if error:
        task["error"] =error
    with open(filepath, "w") as f:
        json.dump(task, f, indent=2)


@dispatch_bp.route("/api/dispatch/stats", methods=["GET"])
def get_stats():
    stats = {}
    for filename in os.listdir(TASK_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(TASK_DIR, filename)
            with open(filepath, "r") as f:
                task = json.load(f)
            client_id = task.get("client_id")
            status = task.get("status")
            if not client_id:
                continue
            if client_id not in stats:
                stats[client_id] = {"total": 0, "success": 0}
            stats[client_id]["total"] += 1
            if status == "success":
                stats[client_id]["success"] += 1

    # 计算百分比
    for cid, data in stats.items():
        total = data["total"]
        success = data["success"]
        data["percent"] = round(success / total * 100, 2) if total > 0 else 0

    return jsonify(stats)






