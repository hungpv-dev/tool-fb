import socket
import platform
import requests
import multiprocessing
 
def get_system_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        local_ip = f"Không lấy được IP cục bộ ({e})"

    try:
        # Sử dụng dịch vụ bên ngoài để lấy IP công khai
        public_ip = requests.get("https://api64.ipify.org?format=json").json()["ip"]
    except Exception as e:
        public_ip = f"Không lấy được IP công khai ({e})"

    return {
        "Hệ điều hành": f"{platform.system()} {platform.release()}",
        "Phiên bản": platform.version(),
        "Kiến trúc": platform.architecture()[0],
        "Tên máy": platform.node(),
        "CPU": platform.processor(),
        "Số lõi CPU": multiprocessing.cpu_count(),
        "Địa chỉ IP cục bộ": local_ip,
        "Địa chỉ IP công khai": public_ip
    }

