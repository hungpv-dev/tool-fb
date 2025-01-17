import threading
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from tools.driver import Browser
from tools.types import push
from time import sleep
from main.root import get_frame
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.login import HandleLogin
from extensions.auth_proxy import create_proxy_extension, check_proxy

def login_page():
    main_frame = get_frame()

    # Tiêu đề trang
    title_label = tk.Label(
        main_frame, text="Đăng nhập tài khoản", font=("Segoe UI", 24, "bold"), bg="#3E4A59", fg="#FFFFFF"
    )
    title_label.pack(pady=20)

    # Hiển thị danh sách tài khoản
    tk.Label(
        main_frame, text="Danh sách tài khoản:", font=("Segoe UI", 16), bg="#f0f2f5"
    ).pack(pady=10)

    # Lấy danh sách tài khoản từ phương thức `account.get_accounts()['data']`
    try:
        from sql.accounts import Account  # Import module chứa hàm lấy tài khoản
        account = Account()
        accounts = account.get_accounts()['data']  # Gọi phương thức lấy danh sách tài khoản
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lấy danh sách tài khoản: {e}")
        accounts = []

    # Hiển thị danh sách tài khoản trong combobox (sử dụng ID cho độ chính xác)
    account_var = tk.StringVar()
    account_combo = ttk.Combobox(
        main_frame, textvariable=account_var, values=[f"{acc['name']} (ID: {acc['id']})" for acc in accounts],
        state="readonly", font=("Segoe UI", 12), width=40
    )
    account_combo.pack(pady=10)
    account_combo.set("Chọn tài khoản")

    # Nút đăng nhập
    def login_selected_account():
        selected_account_info = account_var.get()
        if selected_account_info == "Chọn tài khoản":
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản để đăng nhập!")
            return

        # Lấy ID tài khoản từ tên
        selected_account_id = selected_account_info.split(" (ID: ")[1].replace(")", "")
        selected_account = next(
            (acc for acc in accounts if str(acc['id']) == selected_account_id), None
        )

        if selected_account:
            # Gọi hàm xử lý đăng nhập
            handle_login(selected_account)
        else:
            messagebox.showerror("Lỗi", "Tài khoản không tồn tại!")

    login_button = ttk.Button(
        main_frame,
        text="Đăng nhập",
        style="Custom.TButton",
        command=login_selected_account,
        width=20
    )
    login_button.pack(pady=15)

    # Nút quay lại
    from helpers.base import render
    back_button = ttk.Button(
        main_frame, text="Quay lại", style="Custom.TButton", command=lambda: render('home'),
        width=20
    )
    back_button.pack(pady=10)

    return main_frame

def handle_login(account):
    proxy = account.get('proxy')
    checkProxy = True
    extension = None
    if proxy:
        checkProxy = check_proxy(proxy)
        if checkProxy :
            extension = create_proxy_extension(proxy)

    if checkProxy == True:
        manager = Browser(f"/login/{account['id']}", extension, loadContent=True)
        browser = manager.start(False)
    else:
        messagebox.showerror("Thất bại", f"Proxy không dùng được!")
        return
            
    loginInstance = HandleLogin(browser, account)
    checkLogin = loginInstance.loginFacebook()
    account = loginInstance.getAccount()
    
    if checkLogin == False: 
        try:
            # Đợi phần tử xuất hiện trong 10 phút (600 giây)
            WebDriverWait(browser, 600).until(
                EC.presence_of_element_located((By.XPATH, push['openProfile']))
            )
            save = loginInstance.saveLogin()
            if save:
                messagebox.showerror("Thành công", "Đăng nhập thành công, đã lưu lại cookie!")
        except:
            messagebox.showerror("Thất bại", "Không thể login trong 10 phút!")
            browser.quit()
            return
    else: 
        messagebox.showinfo("Thành công", "Đăng nhập thành công!")

    while True:
        try:
            browser.current_url  # Nếu trình duyệt vẫn mở, sẽ không có lỗi
        except:
            messagebox.showinfo("Thông báo", "Trình duyệt đã đóng!")
            return
        sleep(1)
    
