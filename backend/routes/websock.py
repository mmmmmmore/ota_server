from flask_socketio import SocketIO, emit
import json
import eventlet
eventlet.monkey_patch()
from routes.messagebus import bus

# init obj
socketio = SocketIO(cors_allowed_origins= "*", async_mode="eventlet")



# define the event
@socketio.on("connect")
def handle_connect():
    print("Websocket connected with client")
    
    
@socketio.on("disconnect")
def handle_disconnect():
    print("Websocket disconnect with client")


@socketio.on("query")
def handle_query(payload):
    ##payload sample:
    """_summary_

    {
        "action": "task_summary",
        "client_id":"758"
    }
    """
    action = payload.get("action")
    client_id = payload.get("client_id")




@socketio.on("task_update")
def handle_task_push(data):
    bus.publish("task.create", data)
    


def handle_websocket_message(payload):
    if payload["msg_type"] == "ota_task":
        action = payload["action"]
        if action == "ota_push":
            bus.publish("websock.task_push", payload)
            
            emit("server.response", {
                "request_id": payload.get("request_id"),
                "status": "ok"
            })
        elif action ==  "task_summary":
            bus.publish("websock.task_summary", payload)
        elif action == "tack_history":
            bus.publish("websock.task_history", payload)
        else:
            print("Unknow action from front, please check the js setup")
    elif payload["msg_type"] == "device_info":
        action = payload["action"]
        if action == "create":
            bus.publish("websock.device_create", payload)
        elif action =="delete":
            bus.publish("websock.device_delete", payload)
        elif action =="query":
            bus.publish("websock.device_query", payload)
        elif action == "edit":
            bus.publish("websock.device_edit", payload)
        else:
            print("unknown action from device info, please chekc JS setup")    
    elif payload["msg_type"] == "software_info":
        action = payload["action"]
        if action == "create":
            bus.publish("websock.software_create", payload)
        elif action =="delete":
            bus.publish("websock.software_delete", payload)
        elif action =="query":
            bus.publish("websock.software_query", payload)
        elif action == "edit":
            bus.publish("websock.software_edit", payload)
        else:
            print("unknown action from software info, please chekc JS setup")              
    else:
        print("No valid data rx from front side, please check the js setup")
        

        
        
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
    socketio.emit("page_refresh", {"type": payload.get("type", "generic")})
    #
    # payload example
    print(f"[Web] notify front refresh page: {payload}")
    #
    
def push_task_history(payload):
    socketio.emit("task_history", {"tasks": payload})
    #this transfer the payload as json format to front
    print("[Web] update task history to front finished")


def push_task_summary(payload):
    socketio.emit("task_summary", {"summary_url": payload.get("summary_url")})
    print("[Web] update summary figure path to front, need front udpate the display")
    


def init_websock_subscription():
    bus.subscribe("device.update", notify_refresh)
    bus.subscribe("software.update", notify_refresh)
    ## split
    bus.subscribe("dispatch.task_history", push_task_history)
    bus.subscribe("dispatch.task_summary", push_task_summary)    
