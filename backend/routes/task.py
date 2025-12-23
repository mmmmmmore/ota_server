import matplotlib.pyplot as plt
from enum import IntEnum
import re, os, time
import json
from datetime import datetime
import netifaces
from flask import jsonify
from routes.devices import load_devices
from routes.software import load_software
from routes.base_value import TASK_DIR, STATIC_DIR, SW_LIST_DIR
# setup the target path




os.makedirs(TASK_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
print("from task"+"::"+TASK_DIR)

# define task class

def read_version_note(version):
    swfile = os.path.join(SW_LIST_DIR, "software_list.json")
    with open(swfile, "r", encoding="utf-8") as f:
        data = json.load(f)
    changenotes = next((item["changes"] for item in data if item["version"] == version),None)
    return changenotes



class TaskPhase(IntEnum):
    UNKNOW      = 0x00
    INITIATED   = 0x01
    PENDING     = 0x02
    REJECTED    = 0x03
    FINISHED    = 0x04
    
class TaskResult(IntEnum):
    UNKNOWN     = 0x00
    SUCCESS     = 0x01
    FAILED      = 0x02
    
def to_hex_byte(value: int) -> str :
    return f"0x{value: 02X}"

def parse_hex_byte(hex_str: str) -> int:
    hex_str = hex_str.lower().strip()
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str, 16)


def encode_result(phase: TaskPhase, result: TaskResult) -> str:
    return f"{to_hex_byte(int(phase))} {to_hex_byte(int(result))}"


def decode_result(result_str: str) -> tuple[TaskPhase, TaskResult]:
    parts = result_str.strip().split()
    if len(parts) !=2 :
        return TaskPhase.UNKNOW, TaskResult.UNKNOWN
    phase_val = parts (parts[0])
    result_val = parts(parts[1])
    phase_enum = TaskPhase(phase_val) if phase_val in TaskPhase._value2member_map_ else TaskPhase.UNKNOW
    result_enum = TaskResult(result_val) if result_val in TaskResult._value2member_map_ else TaskResult.UNKNOWN
    return phase_enum, result_enum    







def get_local_ip():
    # try netifaces preferred interface en0 (mac), fallback to UDP trick
    try:
        return netifaces.ifaddresses("en0")[netifaces.AF_INET][0]['addr']
    except Exception:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip




class Task():
    def __init__(self):
        self.taskfolder = TASK_DIR
        self.taskfilelist = []
        self.tasklist = []
        self.devicelist =[]
        
        
        
    def __load_device__(self):
        try:
            self.devicelist = load_devices()
        except json.JSONDecodeError:
            print("device loading error, cannot parse JSON")
            self.devicelist=[]
            
    
    def __load_tasklist__(self):
        pattern_task_id =r'\d{8}_\d{6}_\d{3}\.json'
        #clear the task record before re-load
        self.tasklist=[]
        for filename in os.listdir(TASK_DIR):
            task_remark = re.search(pattern_task_id,filename)
            if task_remark:
                file_path = os.path.join(TASK_DIR, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        task_data = json.load(f)
                        self.tasklist.append(task_data)
                except json.JSONDecodeError:
                    print(f"File {filename} cannot be decoded by JSON")
                except Exception as e:
                    print(f"Cannot read File {filename}")
            else:
                print(f"{TASK_DIR} not exist, please check path")
                
    
    def task_create(self, device_name,client_id, version):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"{timestamp}_{client_id}"
        filename = f"{task_id}.json"
        filepath = os.path.join(TASK_DIR, filename)
        sw_note = read_version_note(version)
        current_ip = get_local_ip()
        task = {
            "msg_type": "ota_task",
            "task_id": task_id,
            "device_name": device_name,
            "client_id": client_id,
            "version": version,
            "firmware_url": f"https://{current_ip}:8080/firmware/ota_client_{client_id}_{version}.bin",
            "timestamp": timestamp,
            "result": encode_result(TaskPhase.INITIATED, TaskResult.UNKNOWN),
            "feature": sw_note
        }
        with open(filepath, "w") as f:
            json.dump(task, f, indent=2)
        self.taskfilelist.append(filepath)
        self.tasklist.append(task)
        return filepath, task
    
    def task_update_phase(self, task_id, new_tashphase: TaskPhase):
        for task in self.tasklist:
            if task["task_id"] == task_id:
                _, current_result = decode_result(task["result"])
                task['result'] = encode_result(new_tashphase, current_result)
                taskfile = os.path.join(TASK_DIR, f"{task_id}.json")
                with open(taskfile, "w") as f:
                    json.dump(task, taskfile, indent=2)
                break
        return None
    
    def task_update_result(self, task_id, new_result: TaskResult):
        for task in self.tasklist:
            if task["task_id"] == task_id:
                current_phase, _ = decode_result(task["result"])
                task["result"] = encode_result(current_phase.FINISHED, new_result)
                taskfile = os.path.join(TASK_DIR, f"{task_id}.json")
                with open(taskfile, "w") as f:
                    json.dump(task, taskfile, indent=2)
                break
        return None
                
                
    
    def __task_summary_by_client(self, client_id):
        result_summary = {
            "total": 0,
            "success":0,
            "failed":0
        }
        phse_summary ={
            "total":0,
            "initiate":0,
            "pending":0,
            "reject":0,
            "finish":0
        }
        if client_id == "all":
            for task in self.tasklist:
                result_summary["total"]+=1
                phase_enum, result_enum = decode_result(task.get("result", "0x00 0x00"))
                if result_enum == TaskResult.SUCCESS:
                    result_summary["success"]+=1
                elif result_enum == TaskResult.FAILED:
                    result_summary["failed"]+=1
                ## after result summary the phase summary
                if phase_enum == TaskPhase.INITIATED:
                    phse_summary["initiate"]+=1
                elif phase_enum == TaskPhase.PENDING:
                    phse_summary["pending"]+=1
                elif phase_enum == TaskPhase.REJECTED:
                    phse_summary["reject"]+=1
                elif phase_enum == TaskPhase.FINISHED:
                    phse_summary["finish"]+=1
        else:
            for task in self.tasklist:
                if task["client_id"] == client_id:
                    continue
                result_summary["total"]+=1
                phase_enum, result_enum = decode_result(task.get("result", "0x00 0x00"))
                if result_enum == TaskResult.SUCCESS:
                    result_summary["success"]+=1
                elif result_enum == TaskResult.FAILED:
                    result_summary["failed"]+=1
                ## after result summary the phase summary
                if phase_enum == TaskPhase.INITIATED:
                    phse_summary["initiate"]+=1
                elif phase_enum == TaskPhase.PENDING:
                    phse_summary["pending"]+=1
                elif phase_enum == TaskPhase.REJECTED:
                    phse_summary["reject"]+=1
                elif phase_enum == TaskPhase.FINISHED:
                    phse_summary["finish"]+=1
            return result_summary, phse_summary

        
    def plot_summary(self, client_id: str, save_dir: str = STATIC_DIR):
        result_summary, phase_summary = self.__task_summary_by_client(client_id)
        
        #plt figure
        fig, axes = plt.subplot(1,2, figsize=(10,4))
        phases = list(phase_summary.keys())
        phase_value = list(phase_summary.values())
        axes[0].bar(phases, phase_value, color="skyblue")
        axes[0].set_title("Task Phase Summary")
        axes[0].set_ylabel("Count")
        for i, v in enumerate(phase_value):
            axes[0].text(i, v+0.1, str(v), ha="center")
        
        results = list(result_summary.keys())
        result_value = list(result_summary.values())
        axes[1].bar(results, result_value, color= "lightgreen")
        axes[1].set_title("Task Result Summary")
        axes[1].set_ylabel("Count")
        for i, v in enumerate(result_value):
            axes[1].text(i, v+0.1, str(v), ha="center")
        
        plt.tight_layout()
        if client_id == "all":        
            save_path = os.path.join(save_dir, f"summary_all.png")
        else:
            save_path = os.path.join(save_dir, f"summary_{client_id}.png")
        plt.savefig(save_path)
        plt.close(fig)
        
        return save_path
        
    def task_history(self, client_id):
        history_tasks=[]
        for task in self.tasklist:
            if task["client_id"] == client_id:
                phase_enum, result_enum = decode_result(task.get("result", "0x00 0x00"))
                history_tasks.append(
                    {
                        "task_id":task["task_id"],
                        "phase":str(phase_enum),
                        "result":str(result_enum)
                    }
                )
        return jsonify(history_tasks)