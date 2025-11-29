from flask import Blueprint, jsonify
import os,json



software_bp = Blueprint("software", __name__)


## JSON save path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR,'..','db')
SOFTWARE_FILE = os.path.join(DB_DIR, "softwares.json")



## initiate check
if not os.path.exists(SOFTWARE_FILE):
    with open(SOFTWARE_FILE, "w") as f:
        json.dump([],f)
        

def load_softwares():
    with open(SOFTWARE_FILE, 'r') as f:
        return json.load(f)
    

def save_softwares(devices):
    with open(SOFTWARE_FILE, 'w') as f:
        json.dump(devices, f, indent=2)





#software_versions = [
#    {"version": "v1.0.0", "date": "2025-11-01", "hardware": "HW_A1", "changes": "初始版本"},
#    {"version": "v1.0.1", "date": "2025-11-05", "hardware": "HW_A1", "changes": "修复网络连接问题"},
#]

@software_bp.route("/api/software", methods=["GET"])
def get_software():
    return jsonify(load_softwares())


