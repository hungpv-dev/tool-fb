import psutil
import inquirer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm


# Hàm lấy danh sách các tiến trình
def get_processes(search_term=""):
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        # Kiểm tra tên tiến trình có chứa từ khóa tìm kiếm (không phân biệt chữ hoa/thường)
        if search_term.lower() in proc.info['name'].lower():
            processes.append(proc.info)
    return processes


# Hàm hiển thị bảng tiến trình
def display_processes(processes):
    table = Table(title="Danh sách Tiến Trình Đang Chạy")
    table.add_column("PID", style="bold green")
    table.add_column("Tên Tiến Trình", style="bold cyan")

    for process in processes:
        table.add_row(str(process['pid']), process['name'])

    console.print(table)


# Hàm cho phép người dùng chọn tiến trình để kill
def choose_process_to_kill(processes):
    # Liệt kê các tiến trình cho người dùng chọn
    process_names = [f"{proc['name']} (PID: {proc['pid']})" for proc in processes]
    questions = [
        inquirer.Text('search', message="Nhập tên tiến trình để tìm kiếm (hoặc để trống để hiển thị tất cả)", default=""),
        inquirer.Checkbox('processes',
                          message="Chọn tiến trình bạn muốn kill",
                          choices=process_names + ["Thoát"],
                          carousel=True,
        ),
    ]
    answers = inquirer.prompt(questions)

    # Kiểm tra xem người dùng có nhập tìm kiếm không, nếu có thì lọc lại
    if answers:
        search_term = answers['search']
        filtered_processes = get_processes(search_term)  # Lọc theo từ khóa tìm kiếm
        if not filtered_processes:
            console.print("Không có tiến trình nào phù hợp với từ khóa tìm kiếm.", style="bold red")
            return

        # display_processes(filtered_processes)

        selected_processes = answers['processes']
        if "Thoát" in selected_processes:
            selected_processes.remove("Thoát")

        if selected_processes:
            for selected_process in selected_processes:
                # Lấy PID từ lựa chọn của người dùng
                pid_to_kill = int(selected_process.split(' (PID: ')[1].split(')')[0])
                kill_confirmation = Confirm.ask(f"Bạn có chắc chắn muốn kill tiến trình {selected_process}?")
                if kill_confirmation:
                    try:
                        process = psutil.Process(pid_to_kill)
                        process.terminate()  # Hoặc dùng process.kill() để dừng ngay lập tức
                        console.print(f"Đã kill tiến trình {selected_process}", style="bold red")
                    except psutil.NoSuchProcess:
                        console.print(f"Tiến trình {pid_to_kill} không tồn tại hoặc đã bị đóng.", style="bold yellow")
        else:
            console.print("Không có tiến trình nào được chọn để kill.", style="bold green")


if __name__ == "__main__":
    console = Console()

    console.print("Xin chào! Đây là công cụ quản lý tiến trình hệ thống.", style="bold blue")

    # Lấy danh sách tiến trình
    processes = get_processes()

    if not processes:
        console.print("Không có tiến trình nào đang chạy.", style="bold red")
    else:
        # Hiển thị bảng tiến trình
        # display_processes(processes)

        # Cho phép người dùng chọn tiến trình để kill
        choose_process_to_kill(processes)
