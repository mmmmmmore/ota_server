from flask import Blueprint, jsonify

software_bp = Blueprint("software", __name__)

software_versions = [
    {"version": "v1.0.0", "date": "2025-11-01", "hardware": "HW_A1", "changes": "初始版本"},
    {"version": "v1.0.1", "date": "2025-11-05", "hardware": "HW_A1", "changes": "修复网络连接问题"},
]

@software_bp.route("/api/software", methods=["GET"])
def get_software():
    return jsonify(software_versions)
