import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "db", "tasks"))


DB_DIR = os.path.join(BASE_DIR,'..','db')
DEVICES_FILE = os.path.join(DB_DIR, "devices.json")


FIRMWARE = os.path.join(BASE_DIR, "..", "firmware")
os.makedirs(TASK_DIR, exist_ok=True)

SOFTWARE_FILE = os.path.join(DB_DIR, "software_list.json")
FIRMWARE_DIR = os.path.join(BASE_DIR, '..', "firmware")


SW_LIST_DIR = os.path.join(BASE_DIR,"..", "db")
STATIC_DIR = os.path.join(BASE_DIR, "..","db","static")

os.makedirs(FIRMWARE_DIR, exist_ok=True)
GW_IP = "192.168.4.1"
GW_TCP_PORT = 9001

SERVERCRT = os.path.join(BASE_DIR, "..", "server.crt")
SERVERKEY = os.path.join(BASE_DIR,"..","server.key")