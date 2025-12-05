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


dispatch_bp = Blueprint("dispatch", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)

GW_IP = "192.168.4.1"
GW_PORT = 9001




class TCPClient:
    """
    长连接 TCP 客户端（用于 OTA Server -> GW 单连接推送）
    Protocol: 4-byte big-endian length prefix + JSON payload (utf-8)
    """

    def __init__(self, host, port, reconnect_interval=3, heartbeat_interval=10):
        self.host = host
        self.port = port
        self.reconnect_interval = reconnect_interval
        self.heartbeat_interval = heartbeat_interval

        self.sock = None
        self.sock_lock = threading.Lock()    # protect sock usage for send/close
        self.running = True

        self.send_q = queue.Queue()
        self.recv_thread = None
        self.sender_thread = None
        self.manager_thread = threading.Thread(target=self._manager_loop, daemon=True)
        self.last_recv = 0

        # start manager
        #self.manager_thread.start()

    def _connect(self):
        """
        Establish connection (blocking). Must be called from manager thread.
        """
        with self.sock_lock:
            try:
                s = socket.create_connection((self.host, self.port), timeout=8)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                s.settimeout(None)  # blocking mode for recv
                self.sock = s
                self.last_recv = time.time()
                print(f"[TCPClient] Connected to {self.host}:{self.port}")
                # spawn recv & sender threads
                self.recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
                self.recv_thread.start()
                if not self.sender_thread or not self.sender_thread.is_alive():
                    self.sender_thread = threading.Thread(target=self._send_loop, daemon=True)
                    self.sender_thread.start()
                return True
            except Exception as e:
                print("[TCPClient] connect failed:", e)
                self.sock = None
                return False

    def _close_sock(self):
        with self.sock_lock:
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None

    def stop(self):
        self.running = False
        self._close_sock()

    def _manager_loop(self):
        """
        Ensure there is one live connection. If lost, reconnect.
        Also send heartbeats periodically (server->gw).
        """
        next_hb = time.time() + self.heartbeat_interval
        while self.running:
            if self.sock is None:
                ok = self._connect()
                if not ok:
                    time.sleep(self.reconnect_interval)
                    continue
            now = time.time()
            # send heartbeat if time
            if now >= next_hb:
                hb = {"msg_type": "keep_alive", "ts": int(now)}
                self.send_json(hb)
                next_hb = now + self.heartbeat_interval
            # detect stale connection (no recv for long time)
            if self.last_recv and (now - self.last_recv) > (self.heartbeat_interval * 4):
                print("[TCPClient] no recv for a while, reconnecting...")
                self._close_sock()
            time.sleep(0.5)

    # ----------------- receive -----------------
    def _recv_loop(self):
        """
        Read length-prefixed messages: 4-byte big-endian len + payload.
        """
        try:
            while self.running and self.sock:
                # read 4 bytes length
                header = self._recv_exact(4)
                if not header:
                    print("[TCPClient] recv header failed (peer closed)")
                    break
                length = struct.unpack("!I", header)[0]
                if length <= 0 or length > 10*1024*1024:
                    print("[TCPClient] bad length", length)
                    break
                data = self._recv_exact(length)
                if not data:
                    print("[TCPClient] recv data failed")
                    break
                self.last_recv = time.time()
                try:
                    msg = json.loads(data.decode("utf-8"))
                except Exception as e:
                    print("[TCPClient] json parse error:", e)
                    continue
                # handle messages
                self._handle_msg(msg)
        except Exception as e:
            print("[TCPClient] recv loop exception:", e)
            traceback.print_exc()
        finally:
            # ensure socket closed and trigger reconnect
            self._close_sock()

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n and self.running:
            with self.sock_lock:
                s = self.sock
            if not s:
                return None
            try:
                chunk = s.recv(n - len(buf))
            except Exception as e:
                # connection error
                return None
            if not chunk:
                return None
            buf += chunk
        return buf

    def _handle_msg(self, msg):
        """
        Handle incoming messages from GW.
        E.g. keep_alive, keep_alive_ack, status updates.
        """
        t = msg.get("msg_type")
        print("[TCPClient] Received", t, msg)
        # update last_recv already set
        if t == "keep_alive":
            # auto ack
            ack = {"msg_type": "keep_alive_ack"}
            self.send_json(ack)
        # other app-specific handling can be placed here

    # ----------------- sending -----------------
    def send_json(self, obj, block=True, timeout=1.0):
        """
        Put message into send queue. Non-blocking push for Flask request handlers.
        """
        try:
            self.send_q.put(obj, block=block, timeout=timeout)
            return True
        except queue.Full:
            return False

    def _send_loop(self):
        """
        Take jsons from queue and send length-prefixed over the single socket.
        """
        while self.running:
            try:
                item = self.send_q.get(timeout=1.0)
            except queue.Empty:
                continue
            payload = json.dumps(item, separators=(",", ":")).encode("utf-8")
            header = struct.pack("!I", len(payload))
            with self.sock_lock:
                s = self.sock
                if not s:
                    # socket died: try re-queue or drop
                    print("[TCPClient] send: no socket, requeue")
                    # requeue at front is tricky; we push back and hope manager reconnects
                    try:
                        self.send_q.put(item, block=False)
                    except:
                        pass
                    time.sleep(0.2)
                    continue
                try:
                    s.sendall(header + payload)
                except Exception as e:
                    print("[TCPClient] sendall error:", e)
                    # close socket to trigger reconnect
                    try:
                        s.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    self._close_sock()
                    # requeue item
                    try:
                        self.send_q.put(item, block=False)
                    except:
                        pass
            # loop continue



# create a global TCPClient instance (will start manager thread)
tcp_client = TCPClient(GW_IP, GW_PORT)

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
    data = request.get_json(force=True)
    device_name = data.get("device_name")
    client_id = data.get("client_id")
    version = data.get("version")
    filepath, task = create_task_file(device_name, client_id, version)

    # simply enqueue task to tcp_client send queue
    ok = tcp_client.send_json(task, block=False)
    if not ok:
        update_task_status(filepath, task, "failed", "send queue full")
        return jsonify({"error": "send queue full"}), 503

    update_task_status(filepath, task, "queued")
    return jsonify({"message": "OTA queued", "task": task}), 200

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
