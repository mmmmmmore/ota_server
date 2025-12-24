# file: routes/dispatch.py
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

import socket
import threading
import time
import struct
import queue
import traceback
import asyncio
from routes.tcp_async import GatewayClient
from routes.task import Task
from routes.base_value import GW_IP, GW_TCP_PORT


dispatch_bp = Blueprint("dispatch", __name__)


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



task_mgmt=Task()
task_mgmt.__load_tasklist__()



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
    filepath, task = task_mgmt.task_create(device_name, client_id, version)

    # simply enqueue task to tcp_client send queue
    try:
        json_str = json.dumps(task)+ "\n"
        # 把任务放入 asyncio 队列，由 TCP 客户端负责发送
        asyncio.run_coroutine_threadsafe(task_queue.put((filepath, task)), loop)
        return jsonify({"message": "OTA Task queued", "task": task}), 200
    except Exception as e:
        update_task_status(filepath, task, "failed", str(e))
        return jsonify({"error": f"Push Err: {str(e)}"}), 500




@dispatch_bp.route("/api/dispatch/state_summary", methods=["GET"])
def get_stats(client_id):
    png = task_mgmt.plot_summary(client_id)
    return {"summary_exeuction":"OK"}


@dispatch_bp.route("/api/dispatch/history/<client_id>", methods=["GET"])
def get_client_history(client_id):
    return task_mgmt.task_history(client_id)


def websock_handle_summary(client_id):
    png = task_mgmt.plot_summary(client_id)
    return {"summary_execution":"OK"}

def websocket_handle_task_history(client_id):
    return task_mgmt.task_history(client_id)