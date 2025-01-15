import tkinter as tk
from main.root import get_root

def setup_menu():
    from helpers.base import render 
    root = get_root()

    """Tạo menu chính."""
    menubar = tk.Menu(root)

    # Trang chủ
    menubar.add_command(label="Trang chủ", command=lambda: render('home'))

    # Lấy bài viết Fanpage
    menubar.add_command(label="Lấy bài viết Fanpage", command=lambda: render('fanpage'))

    # Lấy bài viết Newsfeed
    actions_menu = tk.Menu(menubar, tearoff=0)
    actions_menu.add_command(label="Danh sách", command=lambda: render('newsfeed_page_list'))
    actions_menu.add_command(label="Thêm tiến trình", command=lambda: render('newsfeed'))
    menubar.add_cascade(label="Lấy bài viết Newsfeed", menu=actions_menu)

    # Đăng bài viết
    actions_menu = tk.Menu(menubar, tearoff=0)
    actions_menu.add_command(label="Danh sách", command=lambda: render('post_page_list'))
    actions_menu.add_command(label="Thêm tiến trình", command=lambda: render('post'))
    menubar.add_cascade(label="Đăng bài viết", menu=actions_menu)

    menubar.add_command(label="Đăng nhập", command=lambda: render('login'))
    
    menubar.add_command(label="Cài đặt môi trường", command=lambda: render('settings'))

    menubar.add_command(label="Xem log", command=lambda: render('logs'))

    # Áp dụng menu vào cửa sổ chính
    root.config(menu=menubar)
