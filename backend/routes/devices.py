from flask import Blueprint, jsonify

devices_bp = Blueprint("devices", __name__)

devices = [
    {"name": "Vehicle_1", "ip": "192.168.4.2", "version": "v1.0.0", "partition": "A", "status": "online"},
    {"name": "Vehicle_2", "ip": "192.168.4.3", "version": "v1.0.0", "partition": "A", "status": "online"},
    {"name": "Vehicle_3", "ip": "192.168.4.4", "version": "v1.0.0", "partition": "A", "status": "offline"},
]

@devices_bp.route("/api/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)
