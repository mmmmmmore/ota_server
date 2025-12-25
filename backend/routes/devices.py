import json
import os
from flask import Blueprint, jsonify, request
from routes.base_value import DEVICES_FILE
from routes.messagebus import bus


devices_bp = Blueprint("devices", __name__)

## JSON save path



## initiate check
if not os.path.exists(DEVICES_FILE):
    with open(DEVICES_FILE, "w") as f:
        json.dump([],f)
        

def load_devices():
    with open(DEVICES_FILE, 'r') as f:
        return json.load(f)
    

def save_devices(devices):
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)



def update_device_partition(client_id, ota_result):
    device_info = load_devices
    for d in device_info:
        if d["client_id"] == client_id:
            if ota_result == "success":
                d["partition"] = "B" if d["partition"] =="A" else "A"
            break

                

def update_device_connection(client_id, connect_state):
    device_info = load_devices
    for d in device_info:
        if d["client_id"] == client_id:
            d["status"] = connect_state       ## need html update online/offline.
            break


# 模拟设备存储（后续可以替换成数据库或文件）
#devices = [
#    {"name": "Vehicle_1", "ip": "192.168.4.2", "version": "v1.0.0", "partition": "A", "status": "online"},
#    {"name": "Vehicle_2", "ip": "192.168.4.3", "version": "v1.0.0", "partition": "A", "status": "online"},
#    {"name": "Vehicle_3", "ip": "192.168.4.4", "version": "v1.0.0", "partition": "A", "status": "offline"},
#]

# 查询设备列表
@devices_bp.route("/api/devices", methods=["GET"])
def get_devices():
    devices = load_devices()
    return jsonify(devices)

# 新建设备
@devices_bp.route("/api/devices/register", methods=["POST"])
def register_device():
    data = request.get_json()
    print("Rx Json: ",data)
    if not data or "device_name" not in data or "mac_address" not in data :
        return jsonify({"error": "缺少必要字段"}), 400

    devices = load_devices()
    
    # 检查是否已存在同名或同IP设备
    for d in devices:
        if d["mac_address"] == data["mac_address"] :
            return jsonify({"error": "设备已存在"}), 409

    # 构造新设备
    new_device = {
        "device_name": data["device_name"],
        "mac_address": data["mac_address"],
        "client_id": data.get("client_id"),
        "ip": None,
        "version": data.get("version", "unknown"),
        "partition": None,
        "status": None
    }
    devices.append(new_device)
    save_devices(devices)

    return jsonify(new_device), 201



@devices_bp.route("/api/devices/<mac_address>", methods=["PUT"])
def update_device(mac_address):
    data = request.get_json()
    devices = load_devices()

    for d in devices:
        if d["mac_address"] == mac_address:
            # 更新允许修改的字段
            d["device_name"] = data.get("device_name", d["device_name"])
            d["client_id"] = data.get("client_id", d.get("client_id"))
            d["partition"] = data.get("partition", d.get("partition"))
            save_devices(devices)
            return jsonify(d), 200

    return jsonify({"error": "设备未找到"}), 404



@devices_bp.route("/api/devices/<mac_address>", methods=["DELETE"])
def delete_device(mac_address):
    devices = load_devices()
    new_devices = [d for d in devices if d["mac_address"] != mac_address]

    if len(new_devices) == len(devices):
        return jsonify({"error": "设备未找到"}), 404

    save_devices(new_devices)
    return jsonify({"message": f"设备 {mac_address} 已删除"}), 200




def handle_device_create(payload):
    # payload will include device name, mac and client id...
    devices = load_devices()
    mac = payload.get("mac_address")
    
    if not mac or any(d["mac_address"] == mac for d in devices):
        print(f"[Device] create new device fail, device exist{mac}")
        return
    
    new_devices = {
        "device_name": payload.get("device_name", "Unnamed"),
        "mac_address": mac,
        "client_id": payload.get("client_id"),
        "ip": None,
        "version": payload.get("version", "unknown"),
        "partition": "A",
        "status": None
    }
    
    devices.append(new_devices)
    save_devices(devices)
    print("[Device] New Device created in db")
    
    
def handle_device_delete(payload):
    mac = payload.get("mac_address")
    if not mac:
        print("[Device] device not found by input, please check")
        return

    devices = load_devices()
    new_devices = [d for d in devices if d["mac_address"] != mac]
    save_devices(new_devices)
    print(f" [Device] device of {mac} deleted from db")
    

def handle_device_edit(payload):
    mac = payload.get("mac_address")
    if not mac:
        print("[Device] device not found in db")
        return
    
    devices = load_devices()
    for d in devices:
        if d["mac_address"] == mac:
            d['device_name'] = payload.get("device_name", d["device_name"])
            d['client_id'] = payload.get("client_id", d["client_id"])
            d['partition'] = payload.get("partition", d["partition"])
            save_devices(devices)
            print(f"[Device] device of {mac} updated ")
            break


def handle_device_query(payload):
    devices = load_devices()
    bus.publish("device.update", {"type": "device", "devices": "updated"})
    print("please update info in front")
    

def handle_device_update(payload):
    # change online offline 
    connection = payload.get("online")
    client_id = payload.get("client_id")
    devices = load_devices()
    for d in devices:
        if d["client_id"] = client_id:
            d["status"] = connection
            save_devices(devices)
            print(f"[Device] device {client_id} connection udpated")
            bus.publish("device.update", {"msg_type":"device_update", "content":"connection_changed"})
            break


# need use in app for initialization
def init_device_subscription():
    bus.subscribe("websock.device_create", handle_device_create)
    bus.subscribe("websock.device_delete", handle_device_delete)
    bus.subscribe("websock.device_edit", handle_device_edit)
    bus.subscribe("websock.device_query", handle_device_query)
    bus.subscribe("tcp.device_update", handle_device_update)
        