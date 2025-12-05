# tcpconnect.py
import socket
import threading
import time
import json

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
    return gw_sock
