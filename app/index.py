from helpers.base import render
from pages.menu import setup_menu
from main.root import get_root
from helpers.log import config_log
from helpers.system import init_system,close_system

if __name__ == "__main__":
    init_system()

    config_log()

    root = get_root()

    # Tạo menu
    setup_menu()

    # Hiển thị trang Home ban đầu
    render('home')

    # Khởi động ứng dụng
    root.mainloop()

    close_system()

