import json
import threading
from tkinter import filedialog, messagebox, Toplevel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from main.root import get_frame
import tkinter as tk
from time import sleep
from tkinter import ttk
import os

# Lưu cấu hình (chỉ lưu headless)
def save_configuration(headless_var,omocaptcha_token_var):
    from helpers.base import render

    def save_config(headless_var):
        headless = headless_var.get()
        omocaptcha_token = omocaptcha_token_var.get()

        try:
            # Lưu thông tin cấu hình vào file config.json
            with open("config.json", "r") as config_file:
                config = json.load(config_file)  # Đọc cấu hình hiện tại

            # Cập nhật chỉ trường "headless" mà không thay đổi các thông tin khác
            config["headless"] = headless
            config["omocaptcha_token"] = omocaptcha_token

            with open("config.json", "w") as config_file:
                json.dump(config, config_file, indent=4)
            
            # Thông báo thành công
            messagebox.showinfo("Thành công", "Cấu hình đã được lưu thành công!")
            render('settings')  # Quay lại trang settings
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cấu hình: {str(e)}")

    # Chạy việc lưu cấu hình trong một thread riêng
    threading.Thread(target=save_config, args=(headless_var,), daemon=True).start()

# Tải driver và cập nhật đường dẫn vào cấu hình
def download_driver():
    from helpers.base import render

    # Tạo cửa sổ mới để hiển thị thông báo "Đang tải..."
    loading_window = Toplevel()
    loading_window.title("Đang tải driver...")
    loading_window.geometry("250x100")
    loading_window.configure(bg="#f0f2f5")
    
    loading_label = tk.Label(
        loading_window, text="Đang tải driver, vui lòng đợi...", font=("Segoe UI", 12), bg="#f0f2f5", fg="blue"
    )
    loading_label.pack(expand=True)
    
    def load_driver():
        try:
            # Tải Chrome driver bằng webdriver_manager
            driver_path = ChromeDriverManager().install()

            # Cập nhật đường dẫn driver vào cấu hình mà không thay đổi các thông tin khác
            with open("config.json", "r") as config_file:
                config = json.load(config_file)

            config["driver_path"] = driver_path

            with open("config.json", "w") as config_file:
                json.dump(config, config_file, indent=4)

            # Thông báo thành công
            messagebox.showinfo("Thành công", f"Driver đã được tải và lưu tại: {driver_path}")
            render('settings')  # Quay lại trang settings

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải driver: {str(e)}")
        
        # Đóng cửa sổ loading sau khi tải driver xong
        loading_window.destroy()

    # Chạy việc tải driver trong một thread riêng để không làm đơ giao diện
    threading.Thread(target=load_driver, daemon=True).start()


def start_browser():
    try:
        # Đọc cấu hình
        with open("config.json", "r") as config_file:
            config = json.load(config_file)

        driver_path = config.get("driver_path")
        headless = config.get("headless", True)

        # Kiểm tra driver path có tồn tại không
        if not driver_path or not os.path.exists(driver_path):
            messagebox.showerror("Lỗi", "Không tìm thấy ChromeDriver. Hãy tải driver trước.")
            return

        # Khởi tạo ChromeOptions
        chrome_options = Options()
        if headless == False:
            chrome_options.add_argument("--headless")  # Chạy không giao diện

        # Khởi tạo Service với driver path
        service = Service(driver_path)
        
        # Khởi tạo trình duyệt
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Mở trang chủ
        driver.get("https://www.google.com")

        # Thông báo thành công
        messagebox.showinfo("Thành công", "Trình duyệt đã được khởi động thành công!")

        while True:
            try:
                driver.current_url  # Nếu trình duyệt vẫn mở, sẽ không có lỗi
            except:
                messagebox.showinfo("Thông báo", "Trình duyệt đã đóng!")
                driver.quit()
                return
            sleep(1)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể khởi động trình duyệt: {str(e)}")


# Cập nhật giao diện người dùng với các cấu hình hiện tại
def settings_page():
    main_frame = get_frame()
    from helpers.base import config
    from helpers.base import render

    current_config = config()

    # Tiêu đề trang
    title_label = tk.Label(
        main_frame, text="Cấu hình Đăng nhập", font=("Segoe UI", 20, "bold"), bg="#f0f2f5"
    )
    title_label.pack(pady=20)

    display_current_config(main_frame, current_config)

    # Tùy chọn chế độ headless (Bật/tắt giao diện)
    headless_var = tk.BooleanVar(value=current_config.get("headless", True))
    headless_check = ttk.Checkbutton(
        main_frame, 
        text="Sử dụng giao diện",  # Đổi tên checkbox
        variable=headless_var, 
        style="Custom.TCheckbutton"
    )
    headless_check.pack(pady=5)

    # Thêm ô nhập cho omocaptcha_token
    token_label = tk.Label(
        main_frame, text="OmoCaptcha Token:", font=("Segoe UI", 12), bg="#f0f2f5"
    )
    token_label.pack(pady=5)
    omocaptcha_token_var = tk.StringVar(value=current_config.get("omocaptcha_token", ""))
    token_entry = ttk.Entry(main_frame, textvariable=omocaptcha_token_var, width=100)
    token_entry.pack(pady=5)

    # Khởi tạo frame để chứa các nút
    button_frame = tk.Frame(main_frame, bg="#f0f2f5")
    button_frame.pack(pady=10)

    # Nút lưu cấu hình (chỉ lưu headless)
    save_button = ttk.Button(
        button_frame,
        text="Lưu cấu hình",
        style="Custom.TButton",
        command=lambda: save_configuration(headless_var,omocaptcha_token_var),
        width=15  # Giảm kích thước nút
    )
    save_button.pack(side=tk.LEFT, padx=5)

    # Nút tải driver
    download_button = ttk.Button(
        button_frame,
        text="Tải Driver",
        style="Custom.TButton",
        command=download_driver,
        width=15  # Giảm kích thước nút
    )
    download_button.pack(side=tk.LEFT, padx=5)

    run_browser_button = ttk.Button(
        button_frame,
        text="Chạy Trình Duyệt",
        style="Custom.TButton",
        command=start_browser,
        width=15  # Giảm kích thước nút
    )
    run_browser_button.pack(side=tk.LEFT, padx=5)


    # Button quay lại trang trước đó
    back_button = ttk.Button(
        button_frame, text="Quay lại", style="Custom.TButton", command=lambda: render('home'), width=15
    )
    back_button.pack(side=tk.LEFT, padx=5)

    return main_frame

# Hiển thị cấu hình hiện tại
def display_current_config(main_frame, current_config):
    if current_config:
        # Tạo tiêu đề và bảng hiển thị cấu hình
        tk.Label(main_frame, text="Cấu hình hiện tại:", font=("Segoe UI", 14, "bold"), bg="#f0f2f5", fg="#1c1e21").pack(pady=10)
        
        config_tree = ttk.Treeview(main_frame, columns=("Key", "Value"), show="headings", style="Custom.Treeview")
        config_tree.pack(fill=tk.X, pady=10)
        
        # Định dạng cột và tiêu đề
        config_tree.heading("Key", text="Key", anchor=tk.W)
        config_tree.heading("Value", text="Value", anchor=tk.W)
        config_tree.column("Key", width=200, anchor=tk.W)
        config_tree.column("Value", width=300, anchor=tk.W)
        
        # Thêm dữ liệu vào bảng
        config_tree.insert("", "end", values=("Mở giao diện", "Có" if current_config.get("headless", False) else "Không"))
        config_tree.insert("", "end", values=("Driver path", current_config.get("driver_path", "Chưa có")))
        config_tree.insert("", "end", values=("Omocaptcha Token", current_config.get("omocaptcha_token", "Chưa có")))

        # Cấu hình style
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#f0f2f5", foreground="#000000", fieldbackground="#f0f2f5", rowheight=20)
        style.configure("Custom.Treeview.Heading", background="#4CAF50", foreground="#000000", font=("Segoe UI", 12, "bold"))
        style.map("Custom.Treeview", background=[('selected', '#A9D08E')])
