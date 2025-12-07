from flask import Blueprint, send_from_directory
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "firmware")

download_bp = Blueprint("download", __name__)

@download_bp.route("/firmware/<filename>", methods=["GET"])
def download_firmware(filename):
    # 这里的路径是后端实际存放固件的目录
    return send_from_directory("../firmware", filename)
