from flask_socketio import SocketIO, emit
import json
import eventlet
eventlet.monkey_patch()
from routes.dispatch import websock_handle_summary
from routes.dispatch import websocket_handle_task_history

# init obj
socketio = SocketIO(cors_allowed_origins= "*",async_mode="eventlet")



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
    
    if action == "query_task_history":
        res=websocket_handle_task_history(client_id)
        emit(res)
    elif action == "task_summary":
        res=websock_handle_summary(client_id)
        emit(res)
    else :
        emit("query err",{
            "error": "unknown action",
            "action": action
        })
    