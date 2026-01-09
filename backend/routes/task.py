import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import base64
from threading import Lock, RLock
import re, os, time
import json
from datetime import datetime
import netifaces
from flask import jsonify
from routes.devices import load_devices
from routes.software import load_software
from routes.base_value import TASK_DIR, STATIC_DIR, SW_LIST_DIR
# setup the target path
from routes.base_value import TaskPhase, TaskResult



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




    
def to_hex_byte(value: int) -> str :
    return f"0x{value:02X}"

def parse_hex_byte(hex_str: str) -> int:
    hex_str = hex_str.strip().lower()
    #support "0x01", "01", "1"
    if hex_str.startswith('0x'):
        return int(hex_str, 16)
    return int(hex_str, 16)


def encode_result(phase: TaskPhase, result: TaskResult) -> str:
    return f"{to_hex_byte(int(phase))} {to_hex_byte(int(result))}"


def decode_result(result_str: str) -> tuple[TaskPhase, TaskResult]:
    parts = result_str.strip().split()
    if len(parts) !=2 :
        return TaskPhase.UNKNOWN, TaskResult.UNKNOWN
    
    try:
        phase_int = parse_hex_byte(parts[0])
        result_int = parse_hex_byte(parts[1])
    except ValueError:
        return TaskPhase.UNKNOWN, TaskResult.UNKNOWN
    phase_enum = TaskPhase(phase_int) if phase_int in TaskPhase._value2member_map_ else TaskPhase.UNKNOWN
    result_enum = TaskResult(result_int) if result_int in TaskResult._value2member_map_ else TaskResult.UNKNOWN
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
        self.save_dir = STATIC_DIR
        self._locks ={}
        
    
    def _get_task_lock(self, task_id: str) -> RLock:
        if task_id not in self._locks:
            self._locks[task_id] = RLock()
        return self._locks[task_id]
        
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
            "firmware_url": f"https://192.168.4.2:8443/firmware/ota_client_{client_id}_{version}.bin",
            "timestamp": timestamp,
            "result": encode_result(TaskPhase.INITIATED, TaskResult.UNKNOWN),
            "features": sw_note
        }
        with open(filepath, "w") as f:
            json.dump(task, f, indent=2)
        self.taskfilelist.append(filepath)
        self.tasklist.append(task)
        return filepath, task
    
    def task_update_phase(self, task_id, new_tashphase: TaskPhase):
        lock = self._get_task_lock(task_id)
        with lock:
            for task in self.tasklist:
                if task["task_id"] == task_id:
                    _, current_result = decode_result(task["result"])
                    task['result'] = encode_result(new_tashphase, current_result)
                    taskfile = os.path.join(TASK_DIR, f"{task_id}.json")
                    print(f'[TASK] update task file {taskfile}')
                    with open(taskfile, "w") as f:
                        json.dump(task, f, indent=2)
                        print("[Dispatch] task phase updated")
                    break
        return None
    
    def task_update_result(self, task_id, new_result: TaskResult):
        lock = self._get_task_lock(task_id)
        with lock:
            for task in self.tasklist:
                if task["task_id"] == task_id:
                    current_phase, _ = decode_result(task["result"])
                    task["result"] = encode_result(current_phase.FINISHED, new_result)
                    taskfile = os.path.join(TASK_DIR, f"{task_id}.json")
                    print(f'[TASK] update task file {taskfile}')

                    with open(taskfile, "w") as f:
                        json.dump(task, f, indent=2)
                        print("[Dispatch] task result updated")
                    break
        return None
                
                
    
    def __task_summary_by_client(self, client_id):
        ## below add for debug log
        seq=0
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
        if client_id == "ALL":
            for task in self.tasklist:
                result_summary["total"]+=1
                phse_summary["total"]+=1
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
            print(f"Total of summary is {phse_summary['total']}")
        else:
            for task in self.tasklist:
                if task["client_id"] == client_id:
                    result_summary["total"]+=1
                    phse_summary["total"]+=1
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

        
    def plot_summary(self, client_id: str):
        # Preserve data logic, enhance only visuals
        result_summary, phase_summary = self.__task_summary_by_client(client_id)

        # Friendly display labels keeping original keys
        phase_labels_map = {
            "total": "Total",
            "initiate": "Initiated",
            "pending": "Pending",
            "reject": "Rejected",
            "finish": "Finished",
        }
        result_labels_map = {
            "total": "Total",
            "success": "Success",
            "failed": "Failed",
        }

        # Modern color palette aligned with front theme
        phase_colors_map = {
            "total": "#CBD5E0",     # gray 300
            "initiate": "#667eea",  # indigo
            "pending": "#4299e1",   # blue
            "reject": "#f56565",    # red
            "finish": "#48bb78",    # green
        }
        result_colors_map = {
            "total": "#CBD5E0",
            "success": "#48bb78",
            "failed": "#f56565",
        }

        # Figure setup with a clean, modern style (cross‑platform fonts)
        plt.rcParams.update({
            "font.family": "sans-serif",
            # Use matplotlib-bundled DejaVu Sans first, then common system fonts
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
            "font.size": 11,
            "axes.titleweight": "bold",
            "axes.labelweight": "bold",
        })

        fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))

        # Phases subplot
        phases_keys = list(phase_summary.keys())
        phases_vals = [phase_summary[k] for k in phases_keys]
        phases_labels = [phase_labels_map.get(k, k.title()) for k in phases_keys]
        phases_colors = [phase_colors_map.get(k, "#667eea") for k in phases_keys]

        bars0 = axes[0].bar(phases_labels, phases_vals, color=phases_colors, edgecolor="#e2e8f0", linewidth=1.2)
        axes[0].set_title("Task Phase Summary")
        axes[0].set_ylabel("Count")
        axes[0].grid(axis="y", linestyle="--", alpha=0.35)
        axes[0].spines["top"].set_visible(False)
        axes[0].spines["right"].set_visible(False)

        for rect, v in zip(bars0, phases_vals):
            axes[0].text(
                rect.get_x() + rect.get_width() / 2,
                rect.get_height() + 0.1,
                str(v),
                ha="center",
                va="bottom",
                fontsize=10,
                color="#2d3748",
            )

        # Results subplot
        results_keys = list(result_summary.keys())
        results_vals = [result_summary[k] for k in results_keys]
        results_labels = [result_labels_map.get(k, k.title()) for k in results_keys]
        results_colors = [result_colors_map.get(k, "#667eea") for k in results_keys]

        bars1 = axes[1].bar(results_labels, results_vals, color=results_colors, edgecolor="#e2e8f0", linewidth=1.2)
        axes[1].set_title("Task Result Summary")
        axes[1].set_ylabel("Count")
        axes[1].grid(axis="y", linestyle="--", alpha=0.35)
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)

        for rect, v in zip(bars1, results_vals):
            axes[1].text(
                rect.get_x() + rect.get_width() / 2,
                rect.get_height() + 0.1,
                str(v),
                ha="center",
                va="bottom",
                fontsize=10,
                color="#2d3748",
            )

        # Layout & save
        plt.tight_layout()
        if client_id == "all":
            save_path = os.path.join(self.save_dir, f"summary_all.png")
        else:
            save_path = os.path.join(self.save_dir, f"summary_{client_id}.png")
        plt.savefig(save_path, dpi=160, bbox_inches="tight")
        plt.close(fig)

        with open(save_path, 'rb') as f:
            img_base64 = base64.b64encode(f.read())
            _ = img_base64.decode("ascii")
        return img_base64
        
    def task_history(self, client_id):
        history_tasks=[]
        for task in self.tasklist:
            if task["client_id"] == client_id:
                phase_enum, result_enum = decode_result(task.get("result", "0x00 0x00"))
                history_tasks.append(
                    {
                        "task_id":task["task_id"],
                        "phase":phase_enum.name,
                        "result":result_enum.name
                    }
                )
        return json.dumps(history_tasks)