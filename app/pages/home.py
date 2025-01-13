import tkinter as tk
from tkinter import ttk
from main.root import get_root

def main_page():
    from helpers.base import redirect

    root = get_root()
    # Tạo frame chính (Trang chính)
    main_frame = ttk.Frame(root, padding="10", style="Custom.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew")

    # Thêm Label vào frame chính (Trang chính)
    label = tk.Label(main_frame, text="Chọn hành động của bạn:", font=("Segoe UI", 16), bg="#f0f2f5", fg="#1c1e21")
    label.pack(pady=20)

    button1 = ttk.Button(main_frame, text="Lấy bài viết Fanpage", style="Custom.TButton", command=lambda: redirect('fanpage'))
    button1.pack(fill=tk.X, pady=5, expand=True)

    button2 = ttk.Button(main_frame, text="Lấy bài viết NewsFeed", style="Custom.TButton", command=lambda: redirect('newsfeed'))
    button2.pack(fill=tk.X, pady=5, expand=True)

    button3 = ttk.Button(main_frame, text="Đăng bài viết", style="Custom.TButton", command=lambda: redirect('post'))
    button3.pack(fill=tk.X, pady=5, expand=True)

    button4 = ttk.Button(main_frame, text="Đăng nhập", style="Custom.TButton")
    button4.pack(fill=tk.X, pady=5, expand=True)

    button5 = ttk.Button(main_frame, text="Dọn dẹp bộ nhớ", style="Custom.TButton")
    button5.pack(fill=tk.X, pady=5, expand=True)

    button6 = ttk.Button(main_frame, text="Thoát", style="Custom.TButton")
    button6.pack(fill=tk.X, pady=5, expand=True)

    return main_frame
