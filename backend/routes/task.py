import matplotlib
import re, os, time
import json
from datetime import datetime
from routes.dispatch import get_local_ip

# setup the target path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(BASE_DIR, "..", "db", "tasks")
os.makedirs(TASK_DIR, exist_ok=True)


# define task class





class Task():
    def __init__(self):
        self.taskfolder = TASK_DIR
        self.taskfilelist = []
        self.tasklist = []
        
    def __load_device__(self):
        pass
    
    def __load_tasklist__(self):
        pass
    
    
    def task_create(self, device_name,client_id, version):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"{timestamp}_{client_id}"
        filename = f"{task_id}.json"
        filepath = os.path.join(TASK_DIR, filename)
        current_ip = get_local_ip()
        task = {
            "msg_type": "ota_task",
            "task_id": task_id,
            "device_name": device_name,
            "client_id": client_id,
            "version": version,
            "firmware_url": f"https://{current_ip}:8080/firmware/ota_client_{client_id}_{version}.bin",
            "timestamp": timestamp,
            "status": "initiated"
        }
        with open(filepath, "w") as f:
            json.dump(task, f, indent=2)
        self.taskfilelist.append(filepath)
        self.tasklist.append(task)
        return filepath, task
    
    def task_update(self, task_id, update_state):
        for task in self.tasklist:
            if self.tasklist["task_id"] == task_id:
                self.tasklist['state'] = update_state
                taskfile = os.path.join(TASK_DIR, f"{task_id}.json")
                with open(taskfile, "w") as f:
                    pass
    
    def task_close(self, task_id):
        pass
    
    def task_summary(self, client_id):
        pass
    