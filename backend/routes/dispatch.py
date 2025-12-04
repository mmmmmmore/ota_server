import os
import json
import socket
from datetime import datetime
from flask import Blueprint, request, jsonify
import netifaces
import threading
import time


dispatch_bp = Blueprint("dispatch", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)

GW_IP = "192.168.4.1"
GW_PORT = 9001  # 假设网关监听端口9000
#OTA_Ser_IP = "192.168.4.2"  # server IP
## for long connection and keep alive
gw_sock = None
last_seen = None

def connect_gateway():
    global gw_sock
    while True:
        try:
            gw_sock = socket.create_connection((GW_IP, GW_PORT), timeout=5)
            print("Connected to GW")
            # 启动接收线程
            threading.Thread(target=recv_loop, daemon=True).start()
            break
        except Exception as e:
            print("Connect GW failed:", e)
            time.sleep(5)


def recv_loop():
    global gw_sock, last_seen
    while True:
        try:
            data = gw_sock.recv(1024).decode("utf-8")
            if not data:
                print("GW disconnected")
                gw_sock.close()
                connect_gateway()
                break
            msg = json.loads(data)
            if msg.get("msg_type") == "keep_alive":
                ack = {"msg_type": "keep_alive_ack"}
                gw_sock.sendall(json.dumps(ack).encode("utf-8"))
                last_seen = time.time()
                print("Sent keep_alive_ack to GW")
            else:
                print("GW message:", msg)
        except Exception as e:
            print("Recv loop error:", e)
            gw_sock.close()
            connect_gateway()
            break


def get_ip(interface="en0"):  # Mac 上 Wi-Fi 一般是 en0
    addrs = netifaces.ifaddresses(interface)
    return addrs[netifaces.AF_INET][0]['addr']


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
    current_ip = get_ip()
    #print(get_ip("en0"))  # 应该返回 192.168.4.2
    task = {
        "msg_type":"ota_task",  # msg type for GW msg handler
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
    global gw_sock
    data = request.get_json()
    device_name = data.get("device_name")
    client_id = data.get("client_id")
    version = data.get("version")

    filepath, task = create_task_file(device_name, client_id, version)

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








