import tkinter as tk
from tkinter import ttk
import psutil
from main.root import get_frame

def terminate_process(pid):
    """Kết thúc tiến trình theo PID."""
    try:
        process = psutil.Process(pid)
        process.terminate()
    except Exception as e:
        print(f"Error terminating process {pid}: {e}")

def update_stats(cpu_label, memory_label, disk_label, tree):
    """Cập nhật thông tin hệ thống và danh sách tiến trình theo thời gian thực."""
    cpu_label.config(text=f"CPU Usage: {psutil.cpu_percent()}%")
    memory_info = psutil.virtual_memory()
    memory_label.config(text=f"Memory Usage: {memory_info.percent}% ({memory_info.used // (1024 ** 2)} MB / {memory_info.total // (1024 ** 2)} MB)")
    disk_info = psutil.disk_usage('/')
    disk_label.config(text=f"Disk Usage: {disk_info.percent}% ({disk_info.used // (1024 ** 3)} GB / {disk_info.total // (1024 ** 3)} GB)")

    # Cập nhật danh sách tiến trình
    for item in tree.get_children():
        tree.delete(item)

    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            tree.insert("", "end", values=(
                process.info['pid'],
                process.info['name'],
                f"{process.info['cpu_percent']}%",
                f"{process.info['memory_percent']:.1f}%"
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Lặp lại sau 1 giây
    cpu_label.after(1000, update_stats, cpu_label, memory_label, disk_label, tree)

def on_terminate(tree):
    """Xử lý sự kiện đóng tiến trình khi nhấn nút."""
    selected_item = tree.selection()
    if selected_item:
        pid = int(tree.item(selected_item[0], 'values')[0])
        terminate_process(pid)

def create_close_button(tree, parent_frame):
    """Thêm nút đóng bên cạnh tiến trình."""
    close_button = tk.Button(parent_frame, text="Terminate Process", bg="#d9534f", fg="white", command=lambda: on_terminate(tree))
    close_button.pack(side="right", padx=10)

def main_page():
    stats_frame = get_frame()

    # Nhãn thông tin CPU
    cpu_label = tk.Label(stats_frame, text="CPU Usage: Loading...", font=("Segoe UI", 12), bg="#f0f2f5")
    cpu_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    # Nhãn thông tin Memory
    memory_label = tk.Label(stats_frame, text="Memory Usage: Loading...", font=("Segoe UI", 12), bg="#f0f2f5")
    memory_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    # Nhãn thông tin Disk
    disk_label = tk.Label(stats_frame, text="Disk Usage: Loading...", font=("Segoe UI", 12), bg="#f0f2f5")
    disk_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    # Tạo Treeview để hiển thị danh sách tiến trình
    columns = ("PID", "Name", "CPU %", "Memory %")
    tree = ttk.Treeview(stats_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Tạo nút Terminate Process bên cạnh
    button_frame = tk.Frame(stats_frame, bg="#f0f2f5")
    button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="e")
    create_close_button(tree, button_frame)

    # Cập nhật thông tin hệ thống và tiến trình
    update_stats(cpu_label, memory_label, disk_label, tree)
