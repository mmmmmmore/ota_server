from flask_socketio import SocketIO, emit
import json

# init obj
socketio = SocketIO(cors_allowed_origins= "*",async_mode="gevent")


# define the event
@socketio.on("connect")
def handle_connect():
    print("Websocket connected with client")
    
    
@socketio.on("disconnect")
def handle_disconnect():
    print("Websocket disconnect with client")
    
    
def push_msg_2_front(payload):  ## json format
    message = json.dumps(payload)
    socketio.emit("ota_task_update",message)
    print(f"[WebSocket] pushed ota task update info to front")