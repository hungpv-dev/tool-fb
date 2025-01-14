import requests
from sql.proxy import Proxy
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
import inquirer
import re
console = Console()
proxy_instance = Proxy()

def terminate_processes(processes):
    for process in processes:
        if process.is_alive():
            print(f"Đang dừng tiến trình PID: {process.pid}")
            process.terminate()
            process.join()  # Đảm bảo tiến trình đã dừng hẳn

def get_user_input():
    while True:
        try:
            counts = int(input("Số tab mở để lấy dữ liệu: "))
            return counts
        except ValueError:
            print("Lỗi: Vui lòng nhập một số nguyên hợp lệ.")


def get_list_user_input():
    ids = []
    while True: 
        try:
            user_id = int(input("Nhập ID user bạn muốn thực thi: "))
            if user_id not in ids:
                ids.append(user_id)  
            else:
                print('Bạn đã nhập user này trước đó!')
        except ValueError:
            print("Lỗi: Vui lòng nhập một số nguyên hợp lệ.")
            continue

        check = input("Bạn có muốn tiếp tục không? (y/n): ").strip().lower()
        if check == 'n': 
            break
        elif check != 'y':
            print("Lỗi: Vui lòng chỉ nhập 'y' hoặc 'n'.")
    return ids

      
   
def check_proxy(proxy):
    proxy_ip = proxy['ip']
    proxy_port = proxy['port']
    proxy_username = proxy.get('user')
    proxy_password = proxy.get('pass')
    proxy_auth = f"{proxy_username}:{proxy_password}@" if proxy_username and proxy_password else ""
    proxies = {
        "http": f"http://{proxy_auth}{proxy_ip}:{proxy_port}",
        "https": f"http://{proxy_auth}{proxy_ip}:{proxy_port}",
    }
    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        if response.status_code == 200:
            proxy_instance.update(proxy['id'],{'status':1})
            return True
    except requests.exceptions.RequestException:
        pass
    proxy_instance.update(proxy['id'],{'status':2})
    return False


BOLD_BLUE = '\033[1;34m'  # Màu xanh dương đậm
RED = '\033[31m'
RESET = '\033[0m'


def selected_proxy():
    proxies = proxy_instance.all()['data']

    # Hiển thị spinner (loading)
    with console.status("[bold green]Đang kiểm tra proxy...", spinner="dots") as status:
        proxy_results = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    result = future.result()
                    proxy['result'] = result
                    proxy_results[f"{proxy['ip']}:{proxy['port']}"] = proxy
                except Exception:
                    proxy['result'] = False
                    proxy_results[f"{proxy['ip']}:{proxy['port']}"] = proxy

    # Tạo danh sách proxy với trạng thái
    proxy_choices = []
    for proxy in proxies:
        is_active = proxy_results.get(f"{proxy['ip']}:{proxy['port']}").get('result', False)
        label = f"{proxy['ip']}:{proxy['port']}"
        if is_active:
            proxy_choices.append(label)

    proxy_choices.append("Không sử dụng proxy")

    # Hiển thị danh sách proxy cho người dùng chọn
    proxy_question = inquirer.List(
        'proxy',
        message="Sử dụng proxy",
        choices=proxy_choices,
        carousel=True
    )
    
    proxy_answer = inquirer.prompt([proxy_question])

    select = None
    selected_proxy = proxy_answer['proxy']
    if selected_proxy == 'Không sử dụng proxy': 
        console.print("[bold red]Bạn đã chọn không sử dụng proxy.[/]")
    else:
        select = proxy_results[selected_proxy]
        console.print(f"[bold green]Proxy đã chọn:[/] [bold cyan]{selected_proxy}[/]")

    return select

import os
import shutil
import time
def periodic_cleanup(interval=300):
    while True:
        clear_temp()
        print("[INFO] Đã dọn dẹp thư mục Temp. Chờ 5p để tiếp tục.")
        time.sleep(interval)

def clear_temp():
    temp_dir = os.getenv('TEMP')
    if not temp_dir:
        return
    print(f"Thư mục TEMP hiện tại: {temp_dir}")
    
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        try:
            if os.path.isdir(item_path):  # Kiểm tra xem có phải thư mục không
                shutil.rmtree(item_path)  # Xóa thư mục
                print(f"Đã xóa thư mục: {item_path}")
            else:
                # Không làm gì với file, chỉ xóa thư mục
                pass
        except Exception as e:
            print(f"Không thể xóa {item_path}: {e}")