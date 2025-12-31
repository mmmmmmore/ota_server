# file: routes/dispatch.py


from flask import Blueprint, request, jsonify, current_app

from routes.task import Task
from routes.messagebus import bus
import re


dispatch_bp = Blueprint("dispatch", __name__)

task_mgmt=Task()
task_mgmt.__load_tasklist__()
from routes.base_value import TaskPhase, TaskResult




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



def handle_task_history(payload):
    client_id = payload.get("client_id")
    history_json = task_mgmt.task_history(client_id)
    bus.publish("dispatch.task_history", history_json)
    #print(f"[Dispatch] hisotry json returned")


def handle_task_summary(data):
    client_id = data.get("client_id")
    print(f"[Backend-Dispatch]{client_id} will check the summary")
    png = task_mgmt.plot_summary(client_id)
    bus.publish("dispatch.task_summary", png)
    #print(f"[Dispatch] return png path to front: {png}")
    

def handle_tcp_task_update(payload):
    phase_str , result_str = payload.get("result")
    Task.task_update_phase(phase_str)
    Task.task_update_result(result_str)
    #print("[Dispatch] update the task result, front can check by click the result check :: ")

def handle_task_ack_update(payload):
    # [TCP_Async] Rx task_ack from GW {'msg_type': 'ota_task_ack', 'task_id': '20251231_110325_758', 'status': 'success', 'version': 'v2.3.0'}
    task_id = payload.get("task_id")
    client_id = re.split("_", task_id)[-1] 
    #update task result and phase
    task_mgmt.task_update_phase(task_id, TaskPhase.FINISHED)
    task_mgmt.task_update_result(task_id, TaskResult.SUCCESS)


# this init function use be import to app.py for initialization
def init_dispatch_subscription():
    bus.subscribe("websock.task_push", handle_push_task)
    bus.subscribe("websock.task_history", handle_task_history)
    bus.subscribe("websock.task_summary", handle_task_summary)
    bus.subscribe("tcp.update_task", handle_tcp_task_update)
    bus.subscribe("tcp.update_task", handle_task_ack_update)
    
    
    