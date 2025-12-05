# dispatch.py
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
import netifaces
# tcpconnect.py
import socket
import threading
import time


dispatch_bp = Blueprint("dispatch", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)



GW_IP = "192.168.4.1"
GW_PORT = 9001

gw_sock = None
last_seen = None

def connect_gateway():
    global gw_sock
    while True:
        try:
            gw_sock = socket.create_connection((GW_IP, GW_PORT), timeout=5)
            print("[TCP] Connected to GW")
            threading.Thread(target=recv_loop, daemon=True).start()
            break
        except Exception as e:
            print("[TCP] Connect GW failed:", e)
            time.sleep(5)

def recv_loop():
    global gw_sock, last_seen
    gw_sock.settimeout(15)  # 设置接收超时
    while True:
        try:
            data = gw_sock.recv(1024).decode("utf-8")
            if not data:
                print("[TCP] GW disconnected")
                gw_sock.close()
                connect_gateway()
                break
            msg = json.loads(data)
            if msg.get("msg_type") == "keep_alive":
                ack = {"msg_type": "keep_alive_ack"}
                gw_sock.sendall(json.dumps(ack).encode("utf-8"))
                last_seen = time.time()
                print("[TCP] Sent keep_alive_ack to GW")
            else:
                print("[TCP] GW message:", msg)
        except socket.timeout:
            # 超时不算错误，只是没有数据
            now = time.time()
            if last_seen and (now - last_seen) > 30:
                print("[TCP] No keep_alive for 30s, reconnecting...")
                gw_sock.close()
                connect_gateway()
                break
            else:
                continue
        except Exception as e:
            print("[TCP] Recv loop error:", e)
            gw_sock.close()
            connect_gateway()
            break

def get_socket():
    """提供当前的 GW socket 给外部调用"""
    global gw_sock
    if gw_sock and gw_sock.fileno() != -1 :
        return gw_sock
    return None



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
        payload = json.dumps(task).encode("utf-8")
        print("f[DISPATCH sending OTA task to GW : {task}")
        gw_sock.sendall(payload)
        update_task_status(filepath, task, "success")
        return jsonify({"message": "OTA Push Success", "task": task}), 200
    except Exception as e:
        update_task_status(filepath, task, "failed", str(e))
        return jsonify({"error": f"Push Err: {str(e)}"}), 500

