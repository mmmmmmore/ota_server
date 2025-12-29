# file: routes/dispatch.py


from flask import Blueprint, request, jsonify, current_app

from routes.task import Task
from routes.messagebus import bus


dispatch_bp = Blueprint("dispatch", __name__)

task_mgmt=Task()
task_mgmt.__load_tasklist__()





def handle_push_task(payload):
    device_name = payload.get("device_name")
    client_id = payload.get("client_id")
    version = payload.get("version")
    filepath, task = task_mgmt.task_create(device_name, client_id, version)
    # simply enqueue task to tcp_client send queue
    try:
        bus.publish("dispatch.task_send", {'filepath':filepath,'task_json':task})
        print(task)
    except Exception as e:
        bus.publish("task.failed", {"task":task, "error":str(e)})  ## reverse 




@dispatch_bp.route("/api/dispatch/state_summary", methods=["GET"])
def get_stats(client_id):
    png = task_mgmt.plot_summary(client_id)
    return {"summary_exeuction":"OK"}


@dispatch_bp.route("/api/dispatch/history/<client_id>", methods=["GET"])
def get_client_history(client_id):
    return task_mgmt.task_history(client_id)



def handle_task_history(client_id):
    history_json = task_mgmt.task_history(client_id)
    bus.publish("dispatch.task_history", history_json)
    print(f"[Dispatch] hisotry json returned")


def handle_task_summary(data):
    png = task_mgmt.plot_summary(data)
    bus.publish("dispatch.task_summary", png)
    print(f"[Dispatch] return png path to front: {png}")
    

def handle_tcp_task_update(payload):
    phase_str , result_str = payload.get("result")
    Task.task_update_phase(phase_str)
    Task.task_update_result(result_str)
    print("[Dispatch] update the task result, front can check by click the result check :: ")

# this init function use be import to app.py for initialization
def init_dispatch_subscription():
    bus.subscribe("websock.task_push", handle_push_task)
    bus.subscribe("websock.task_history", handle_task_history)
    bus.subscribe("websock.task_summary", handle_task_summary)
    bus.subscribe("tcp.update_task", handle_tcp_task_update)
    
    
    