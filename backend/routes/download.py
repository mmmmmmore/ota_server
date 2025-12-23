from flask import Blueprint, send_from_directory
import os
download_bp = Blueprint("download", __name__)

from routes.base_value import FIRMWARE



@download_bp.route("/firmware/<filename>", methods=["GET"])
def download_firmware(filename):
    # 这里的路径是后端实际存放固件的目录
    return send_from_directory(FIRMWARE, filename)
