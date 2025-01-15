import tkinter as tk
from tkinter import scrolledtext
from main.root import get_frame
from helpers.log import read_log
import os

# Biến toàn cục để lưu cửa sổ log và đối tượng ScrolledText
log_window = None
log_text = None

# Hàm xóa nội dung file log
def clear_log(log_dir='./temp/logs', log_filename='error.log'):
    """
    Xóa toàn bộ nội dung file log.
    log_dir: Thư mục chứa file log.
    log_filename: Tên file log.
    """
    log_file_path = os.path.join(log_dir, log_filename)
    try:
        # Kiểm tra nếu file log tồn tại
        if os.path.exists(log_file_path):
            with open(log_file_path, 'w', encoding='utf-8') as file:
                file.write("")  # Xóa nội dung bằng cách ghi rỗng
        else:
            print("Log file does not exist.")
    except Exception as e:
        print(f"Error clearing log file: {str(e)}")

def update_log():
    """Cập nhật nội dung log trong cửa sổ log mỗi giây."""
    if log_window and log_text:
        log_content = read_log()  # Đọc lại nội dung log mới
        log_text.delete(1.0, tk.END)  # Xóa nội dung cũ
        log_text.insert(tk.END, log_content)  # Ghi lại nội dung mới
        log_text.yview(tk.END)  # Cuộn xuống cuối cùng

    # Đặt lại hàm update_log để gọi lại sau 1000 ms (1 giây)
    if log_window and log_window.winfo_exists():
        log_window.after(1000, update_log)

def logs_page():
    global log_window, log_text

    # Nếu cửa sổ log chưa được tạo, tạo mới
    if log_window is None or not log_window.winfo_exists():
        frame = get_frame()

        # Tạo cửa sổ mới để hiển thị log
        log_window = tk.Toplevel(frame)
        log_window.title("Log")

        # Thêm ScrolledText để hiển thị log
        log_text = scrolledtext.ScrolledText(log_window, width=100, height=30)
        log_text.pack(padx=10, pady=10)

        # Tạo nút Clear Log
        clear_button = tk.Button(log_window, text="Clear Log", command=lambda: clear_log_and_update())
        clear_button.pack(pady=5)

        # Gọi hàm cập nhật log ban đầu
        update_log()
    else:
        # Nếu cửa sổ log đã tồn tại, chỉ làm mới nội dung
        log_window.lift()  # Đưa cửa sổ log lên trên

def clear_log_and_update():
    """Xóa nội dung log và làm mới cửa sổ hiển thị log."""
    clear_log()  # Xóa nội dung log
    if log_text:
        log_text.delete(1.0, tk.END)  # Xóa nội dung trong ScrolledText
