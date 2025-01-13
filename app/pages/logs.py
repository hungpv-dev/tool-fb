import tkinter as tk
from tkinter import scrolledtext
from main.root import get_root

def logs_page():
    root = get_root()
    # Tạo cửa sổ mới để hiển thị log
    log_window = tk.Toplevel(root)
    log_window.title("Log")

    # Thêm ScrolledText để hiển thị log
    log_text = scrolledtext.ScrolledText(log_window, width=100, height=30)
    log_text.pack(padx=10, pady=10)

    # Ghi log mẫu
    log_text.insert(tk.END, "Đây là log\n")
    log_text.insert(tk.END, "Log sẽ được cập nhật ở đây...\n")
    log_text.yview(tk.END)