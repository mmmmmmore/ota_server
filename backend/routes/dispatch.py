# file: routes/dispatch.py
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
import netifaces
import socket
import threading
import time
import struct
import queue
import traceback
import asyncio
from routes.tcp_async import GatewayClient

dispatch_bp = Blueprint("dispatch", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)


GW_IP = "192.168.4.1"
GW_TCP_PORT = 9001
task_queue = None
loop = None

def start_asyncio():
    global loop, task_queue
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task_queue = asyncio.Queue()
    client = GatewayClient(GW_IP, GW_TCP_PORT, task_queue)
    loop.run_until_complete(client.run())

tcpthread = threading.Thread(target= start_asyncio, daemon=True )







def get_local_ip():
    # try netifaces preferred interface en0 (mac), fallback to UDP trick
    try:
        return netifaces.ifaddresses("en0")[netifaces.AF_INET][0]['addr']
    except Exception:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
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
    current_ip = get_local_ip()
    task = {
        "msg_type": "ota_task",
        "task_id": task_id,
        "device_name": device_name,
        "client_id": client_id,
        "version": version,
        "firmware_url": f"https://{current_ip}:8080/firmware/ota_client_{version}.bin",
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
    data = request.get_json(force=True)
    device_name = data.get("device_name")
    client_id = data.get("client_id")
    version = data.get("version")
    filepath, task = create_task_file(device_name, client_id, version)

    # simply enqueue task to tcp_client send queue
    try:
        # 把任务放入 asyncio 队列，由 TCP 客户端负责发送
        asyncio.run_coroutine_threadsafe(task_queue.put((filepath, task)), loop)
        return jsonify({"message": "OTA Task queued", "task": task}), 200
    except Exception as e:
        update_task_status(filepath, task, "failed", str(e))
        return jsonify({"error": f"Push Err: {str(e)}"}), 500




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
    for cid, data in stats.items():
        total = data["total"]
        success = data["success"]
        data["percent"] = round(success / total * 100, 2) if total > 0 else 0
    return jsonify(stats)

