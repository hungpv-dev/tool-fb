import json
import threading
from tkinter import filedialog, messagebox, Toplevel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from main.root import get_frame
import tkinter as tk
from tkinter import ttk

def save_configuration(browser_var, headless_var):
    from helpers.base import render

    def load_browser(browser_var, headless_var):
        browser_type = browser_var.get()
        headless = headless_var.get()

        try:
            # Tải driver Chrome tự động bằng webdriver_manager
            if browser_type == 'chrome':
                driver_path = ChromeDriverManager().install()

            # Lưu thông tin cấu hình vào file config.json
            config = {
                "browser": browser_type,
                "headless": headless,
                "driver_path": driver_path
            }

            with open("config.json", "w") as config_file:
                json.dump(config, config_file, indent=4)

            # Khởi tạo và chạy trình duyệt
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Thông báo thành công và quay lại trang chủ
            messagebox.showinfo("Thành công", "Cấu hình thành công! Trình duyệt đã được khởi động.")
            render('home')  # Quay lại trang chủ sau khi cài đặt xong
            loading_window.destroy()  # Đóng cửa sổ loading khi hoàn thành

        except Exception as e:
            loading_window.destroy()  # Đóng cửa sổ loading khi có lỗi
            messagebox.showerror("Lỗi", f"Không thể khởi động trình duyệt: {str(e)}")

    # Tạo cửa sổ loading
    loading_window = Toplevel()
    loading_window.title("Đang tải...")
    loading_window.geometry("200x100")
    loading_label = tk.Label(loading_window, text="Đang tải trình duyệt...", font=("Segoe UI", 12))
    loading_label.pack(pady=30)

    # Chạy việc tải và khởi động trình duyệt trong một thread riêng
    threading.Thread(target=load_browser, args=(browser_var, headless_var), daemon=True).start()

def settings_page():
    main_frame = get_frame()
    label = tk.Label(main_frame, text="Trang chủ", font=("Segoe UI", 20), bg="#f0f2f5")
    label.pack(pady=20)
    from helpers.base import config
    from helpers.base import render

    current_config = config()

    # Thêm Label vào frame chính (Trang cấu hình)
    label = tk.Label(main_frame, text="Cấu hình môi trường trình duyệt:", font=("Segoe UI", 16), bg="#f0f2f5", fg="#1c1e21")
    label.pack(pady=20)

    display_current_config(main_frame,current_config)


    # Chọn trình duyệt (Chrome, Firefox, Edge)
    browser_label = tk.Label(main_frame, text="Chọn trình duyệt:", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
    browser_label.pack(pady=5)
    
    browser_var = tk.StringVar(value='chrome')
    browser_options = ttk.Combobox(main_frame, textvariable=browser_var, values=["chrome", "firefox", "edge"], state="readonly")
    browser_options.pack(fill=tk.X, pady=5)
    
    # Chế độ headless (Ẩn giao diện trình duyệt)
    headless_var = tk.BooleanVar(value=True)
    headless_check = ttk.Checkbutton(main_frame, text="Chế độ headless", variable=headless_var, style="Custom.TCheckbutton")
    headless_check.pack(pady=5)

    save_button = ttk.Button(main_frame, text="Lưu cấu hình và khởi động", style="Custom.TButton", command=lambda: save_configuration(browser_var, headless_var))
    save_button.pack(fill=tk.X, pady=10, expand=True)

    # Button quay lại trang trước đó
    back_button = ttk.Button(main_frame, text="Quay lại", style="Custom.TButton", command=lambda: render('home'))
    back_button.pack(fill=tk.X, pady=5)

    return main_frame

def display_current_config(main_frame, current_config):
    if current_config:
        # Tiêu đề "Cấu hình hiện tại"
        current_config_label = tk.Label(main_frame, text="Cấu hình hiện tại:", font=("Segoe UI", 14, "bold"), bg="#f0f2f5", fg="#1c1e21")
        current_config_label.pack(pady=10)

        # Tạo bảng (Treeview) để hiển thị cấu hình
        config_tree = ttk.Treeview(main_frame, columns=("Key", "Value"), show="headings", style="Custom.Treeview")
        config_tree.pack(fill=tk.X, pady=10)

        # Định dạng tiêu đề cột
        config_tree.heading("Key", text="Key", anchor=tk.W)
        config_tree.heading("Value", text="Value", anchor=tk.W)
        
        # Định dạng cột
        config_tree.column("Key", width=200, anchor=tk.W)
        config_tree.column("Value", width=300, anchor=tk.W)
        
        # Thêm dữ liệu vào bảng
        config_tree.insert("", "end", values=("Trình duyệt", current_config.get("browser", "Chưa có")))
        config_tree.insert("", "end", values=("Chế độ headless", "Có" if current_config.get("headless", False) else "Không"))
        config_tree.insert("", "end", values=("Driver path", current_config.get("driver_path", "Chưa có")))

        # Tùy chỉnh border cho bảng
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                        background="#f0f2f5", 
                        foreground="#1c1e21", 
                        fieldbackground="#f0f2f5", 
                        rowheight=30)
        style.configure("Custom.Treeview.Heading", 
                        background="#4CAF50", 
                        foreground="white", 
                        font=("Segoe UI", 12, "bold"))
        style.map("Custom.Treeview", background=[('selected', '#A9D08E')])  # Màu khi chọn dòng

