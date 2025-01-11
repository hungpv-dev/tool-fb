import tkinter as tk
from tkinter import ttk
from helpers.base import redirect
from main.root import get_root

def create_facebook_like_interface():
    root = get_root(True)

    # Lúc đầu, hiển thị trang chính (main_frame)
    redirect('home')

    # Chạy vòng lặp chính của giao diện
    root.mainloop()

# Gọi hàm để tạo giao diện đẹp
create_facebook_like_interface()