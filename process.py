import psutil
import inquirer
from rich.console import Console
from rich.prompt import Confirm

# Hàm lấy danh sách các tiến trình với thông tin sử dụng RAM
def get_processes(search_term=""):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # Kiểm tra tên tiến trình có chứa từ khóa tìm kiếm (không phân biệt chữ hoa/thường)
            if search_term.lower() in proc.info['name'].lower():
                memory_usage_mb = proc.info['memory_info'].rss / (1024 * 1024)  # Chuyển từ byte sang MB
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory': memory_usage_mb
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

# Hàm cho phép người dùng chọn tiến trình để kill
def choose_process_to_kill():
    console = Console()

    # Nhập từ khóa tìm kiếm từ người dùng
    search_term = console.input("[bold blue]Nhập tên tiến trình để tìm kiếm (hoặc để trống để hiển thị tất cả): [/]")

    # Lấy danh sách tiến trình phù hợp
    processes = get_processes(search_term)

    if not processes:
        console.print("[bold red]Không có tiến trình nào phù hợp với từ khóa tìm kiếm.[/]")
        return

    # Liệt kê các tiến trình với thông tin RAM
    process_choices = [
        f"{proc['name']} (PID: {proc['pid']}, RAM: {proc['memory']:.2f} MB)"
        for proc in processes
    ]

    process_choices.append("Thoát")

    # Hiển thị danh sách tiến trình để người dùng chọn
    questions = [
        inquirer.Checkbox('selected_processes',
                          message="Chọn tiến trình bạn muốn kill",
                          choices=process_choices)
    ]

    answers = inquirer.prompt(questions)

    if not answers or "Thoát" in answers['selected_processes']:
        console.print("[bold green]Thoát chương trình quản lý tiến trình.[/]")
        return

    # Xử lý tiến trình được chọn
    for selected_process in answers['selected_processes']:
        try:
            # Lấy PID từ chuỗi mô tả tiến trình
            pid_to_kill = int(selected_process.split(' (PID: ')[1].split(',')[0])
            
            # Xác nhận kill tiến trình
            kill_confirmation = Confirm.ask(f"Bạn có chắc chắn muốn kill tiến trình {selected_process}?")
            if kill_confirmation:
                process = psutil.Process(pid_to_kill)
                process.terminate()  # Hoặc dùng process.kill() để dừng ngay lập tức
                console.print(f"[bold red]Đã kill tiến trình {selected_process}[/]")
        except psutil.NoSuchProcess:
            console.print(f"[bold yellow]Tiến trình {pid_to_kill} không tồn tại hoặc đã bị đóng.[/]")
        except Exception as e:
            console.print(f"[bold red]Lỗi khi xử lý tiến trình {selected_process}: {str(e)}[/]")

if __name__ == "__main__":
    console = Console()

    console.print("[bold blue]Xin chào! Đây là công cụ quản lý tiến trình hệ thống.[/]")

    # Cho phép người dùng chọn tiến trình để kill
    choose_process_to_kill()