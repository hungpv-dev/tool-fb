import tkinter as tk

from main.root import get_frame

def main_page():
    frame = get_frame()
    """Hiển thị nội dung trang Home."""
    label = tk.Label(frame, text="Trang chủ", font=("Segoe UI", 20), bg="#f0f2f5")
    label.pack(pady=20)
