from helpers.base import render
import tkinter as tk
from pages.menu import setup_menu
from main.root import get_root
from helpers.log import config_log
import logging


if __name__ == "__main__":
    config_log()

    root = get_root()

    # Tạo menu
    setup_menu()

    # Hiển thị trang Home ban đầu
    render('home')

    # Khởi động ứng dụng
    root.mainloop()

