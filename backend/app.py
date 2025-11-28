from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# 固件存储目录
FIRMWARE_DIR = os.path.join(os.path.dirname(__file__), "../firmware")
os.makedirs(FIRMWARE_DIR, exist_ok=True)

# 模拟设备列表
devices = [
    {"name": "Vehicle_1", "ip": "192.168.4.2", "version": "v1.0.0", "partition": "A", "status": "online"},
    {"name": "Vehicle_2", "ip": "192.168.4.3", "version": "v1.0.0", "partition": "A", "status": "online"},
    {"name": "Vehicle_3", "ip": "192.168.4.4", "version": "v1.0.0", "partition": "A", "status": "offline"},
]

# 模拟软件版本列表
software_versions = [
    {"version": "v1.0.0", "date": "2025-11-01", "hardware": "HW_A1", "changes": "初始版本"},
    {"version": "v1.0.1", "date": "2025-11-05", "hardware": "HW_A1", "changes": "修复网络连接问题"},
    {"version": "v1.1.0", "date": "2025-11-10", "hardware": "HW_A2", "changes": "增加OTA日志功能"},
    {"version": "v1.2.0", "date": "2025-11-15", "hardware": "HW_A2", "changes": "优化内存管理"},
]

# 模拟任务状态
task_results = {}

# ---------------- API 路由 ---------------- #

@app.route("/api/devices", methods=["GET"])
def get_devices():
    return jsonify(devices)

@app.route("/api/software", methods=["GET"])
def get_software():
    return jsonify(software_versions)

@app.route("/api/upload", methods=["POST"])
def upload_firmware():
    file = request.files.get("file")
    version = request.form.get("version", "unknown")
    if file:
        filepath = os.path.join(FIRMWARE_DIR, "firmware.bin")
        file.save(filepath)
        software_versions.append({
            "version": version,
            "date": "2025-11-28",
            "hardware": "HW_Ax",
            "changes": "新上传版本"
        })
        print(jsonify({"status":"ok", "version":version}))
        return jsonify({"status": "ok", "version": version})
    return jsonify({"status": "fail"}), 400


@app.route("/firmware/<filename>", methods=["GET"])
def get_firmware(filename):
    return send_from_directory(FIRMWARE_DIR, filename)

@app.route("/api/dispatch", methods=["POST"])
def dispatch_task():
    data = request.json
    target = data.get("target", [])
    version = data.get("version")
    url = data.get("url")

    task_id = str(len(task_results) + 1)
    task_results[task_id] = []

    # 模拟任务下发
    for dev in devices:
        if dev["name"] in target:
            dev["status"] = "updating"
            dev["version"] = version
            task_results[task_id].append({"name": dev["name"], "result": "pending"})

    return jsonify({"status": "dispatched", "task_id": task_id})

@app.route("/api/status", methods=["GET"])
def get_status():
    task_id = request.args.get("task_id")
    if task_id and task_id in task_results:
        # 模拟结果更新
        for res in task_results[task_id]:
            if res["result"] == "pending":
                res["result"] = "success"  # 简化：直接成功
        return jsonify(task_results[task_id])
    return jsonify({"status": "no task"}), 404

# ---------------- 主入口 ---------------- #
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
