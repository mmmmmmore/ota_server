from flask_socketio import SocketIO, emit
from flask import request
import json
#import eventlet
#eventlet.monkey_patch()
from routes.messagebus import bus

# init obj
socketio = SocketIO(cors_allowed_origins= "*", async_mode="threading")






def handle_server_response(payload):
    payload_ack = {
        "msg_type":payload.get("msg_type"),
        "request_id":payload.get("request_id"),
        "status": "ok"
    }
    emit("server.response", payload_ack)
    #print(payload_ack)

def handle_ota_task_message(payload):
    action = payload["action"]
    if action == "pushtask":
        #print("exe the task publish")
        bus.publish("websock.task_push", payload)    
        handle_server_response(payload)
    elif action ==  "queryTaskSummary":
        bus.publish("websock.task_summary", payload)
        handle_server_response(payload)
    elif action == "queryTasklist":
        bus.publish("websock.task_history", payload)
        handle_server_response(payload)
    else:
        print("Unknow action from front, please check the js setup")
    

def handle_device_message(payload):
    action = payload["action"]
    if action == "device_create":
        bus.publish("websock.device_create", payload)
        handle_server_response(payload)
    elif action =="device_delete":
        bus.publish("websock.device_delete", payload)
        handle_server_response(payload)
    elif action =="device_query":
        bus.publish("websock.device_query", payload)
        handle_server_response(payload)
    elif action == "device_edit":
        bus.publish("websock.device_edit", payload)
        handle_server_response(payload)
    else:
        print("unknown action from device info, please chekc JS setup")    



def handle_software_message(payload):
    action = payload["action"]
    if action == "software_create":
        
        bus.publish("websock.software_create", payload)
        handle_server_response(payload)
    elif action =="software_delete":
        bus.publish("websock.software_delete", payload)
        handle_server_response(payload)
    elif action =="software_query":
        bus.publish("websock.software_query", payload)
        handle_server_response(payload)
    elif action == "software_edit":
        bus.publish("websock.software_edit", payload)
        handle_server_response(payload)
    else:
        print("unknown action from software info, please chekc JS setup")       



def handle_websocket_message(payload):
    print(payload["msg_type"])
    if payload["msg_type"] == "task_info":
        #print("exe the task handle")
        handle_ota_task_message(payload)
    elif payload["msg_type"] == "device_info":
        handle_device_message(payload)
    elif payload["msg_type"] == "software_info":
        handle_software_message(payload)
    else:
        print("[HANDLE_WEB]::No valid data rx from front side, please check the js setup")
        




## front and backend routes definition.
# define the event
@socketio.on("connect")
def handle_connect():
    print("Websocket connected with client")
    
    
@socketio.on("disconnect")
def handle_disconnect():
    print("Websocket disconnect with client")

    

@socketio.on("heartbeat")
def handle_heartbeat(data):
    print(f" HB from {request.sid} at {data['ts']}")
    emit("heartbeat_ack", {"status":"OK", "ts":data["ts"]}, to=request.sid)

        
@socketio.on("client.request")
def handle_client_request(payload):
    print("[WS] rx client.request:", payload)

    try:
        handle_websocket_message(payload)
    except Exception as e:
        emit("server.response", {
            "request_id": payload.get("request_id"),
            "status": "error",
            "error": str(e)
        })

     
        
def notify_refresh(payload):
    socketio.emit("server.parsed", {
        "msg_type":"ota_server_notify",
        "action":"fresh",
        "payload":payload
    })
    #
    # payload example
    print(f"[Web] notify front refresh page: {payload}")
    #
    
def push_task_history(payload):
    socketio.emit("server.parsed", {
        "msg_type":"ota_history_list",
        "action":"response_history_list",
        "subarea":"task_history",
        "payload":payload
    })
    #print("[Backend-WEB]:", payload)
    #this transfer the payload as json format to front
    print("[Web] update task history to front finished")


def push_task_summary(payload):
    socketio.emit("server.parsed", {
        "msg_type":"ota_task_summary",
        "action":"response_url",
        "url":payload   # url of png 
    })
    print("[Web] update summary figure path to front, need front udpate the display")
    


def init_websock_subscription():
    bus.subscribe("device.update", notify_refresh)
    bus.subscribe("software.update", notify_refresh)
    ## split
    bus.subscribe("dispatch.task_history", push_task_history)
    bus.subscribe("dispatch.task_summary", push_task_summary)    



