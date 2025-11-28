from flask import Blueprint, request, jsonify

dispatch_bp = Blueprint("dispatch", __name__)
task_results = {}

@dispatch_bp.route("/api/dispatch", methods=["POST"])
def dispatch_task():
    data = request.json
    target = data.get("target", [])
    version = data.get("version")
    url = data.get("url")

    task_id = str(len(task_results) + 1)
    task_results[task_id] = [{"name": t, "result": "pending"} for t in target]

    return jsonify({"status": "dispatched", "task_id": task_id})

@dispatch_bp.route("/api/status", methods=["GET"])
def get_status():
    task_id = request.args.get("task_id")
    if task_id in task_results:
        for res in task_results[task_id]:
            if res["result"] == "pending":
                res["result"] = "success"  # 简化逻辑：直接成功
        return jsonify(task_results[task_id])
    return jsonify({"status": "no task"}), 404
