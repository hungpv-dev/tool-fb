import tkinter as tk
from tkinter import ttk
from main.root import get_root
from sql.accounts import Account
from main.post import get_post_process_instance
from tools.facebooks.browser_post import process_post
import threading

post_process_instance = get_post_process_instance()

def newfeedhandle(selected_accounts):
    try:
        for account in selected_accounts:
            print(account.get('name'))
            stop_event = threading.Event()
            thread = threading.Thread(target=process_post, args=(account, stop_event))
            thread.start()
            account['stop_event'] = stop_event
            account['tasks'] = [thread]
            account['status_process'] = 1 # 1: Hoạt động, 2: Đã đóng
            post_process_instance.add_process(account)
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")

def post_page():
    account_sql = Account()
    root = get_root()
    from helpers.base import redirect
    frame = ttk.Frame(root, padding="10", style="Custom.TFrame")
    frame.grid(row=0, column=0, sticky="nsew")

    account_selected = post_process_instance.get_all_processes()

    # Hàm lấy danh sách tài khoản từ API và hiển thị
    def fetch_and_display_accounts(search_keyword=None):
        params = {'typenot': 1}
        if search_keyword:
            params['name'] = search_keyword
        accounts = account_sql.get_accounts(params)['data']


        # Xóa tất cả các checkbox hiện tại
        for widget in checkbutton_frame.winfo_children():
            widget.destroy()

        # Hiển thị các checkbox mới
        for account in accounts:
            if account.get('id') in account_selected:
                continue

            var = tk.BooleanVar()
            cb = ttk.Checkbutton(checkbutton_frame, text=account["name"], variable=var, style="Custom.TCheckbutton")
            cb.pack(anchor="w", padx=20, pady=2)
            checkboxes[account["id"]] = {"checkbox_var": var, "account_data": account}

    # Hiển thị danh sách tài khoản
    label = tk.Label(frame, text="Chọn tài khoản:", font=("Segoe UI", 14), bg="#f0f2f5", fg="#1c1e21")
    label.pack(pady=10)

    # Tạo danh sách checkbox
    checkboxes = {}
    checkbutton_frame = ttk.Frame(frame)
    checkbutton_frame.pack(fill=tk.BOTH, expand=True)

    fetch_and_display_accounts()  # Hiển thị tất cả tài khoản ban đầu

    # Thanh tìm kiếm
    search_var = tk.StringVar()

    def search_accounts():
        keyword = search_var.get().strip()
        fetch_and_display_accounts(keyword)




    search_frame = ttk.Frame(frame)
    search_frame.pack(fill=tk.X, pady=5)

    search_entry = ttk.Entry(search_frame, textvariable=search_var, style="Custom.TEntry")
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    search_button = ttk.Button(search_frame, text="Tìm kiếm", style="Custom.TButton", command=search_accounts)
    search_button.pack(side=tk.LEFT, padx=5)

    # Nút xác nhận
    def submit_selection():
        selected_accounts = [data["account_data"] for account_id, data in checkboxes.items() if data["checkbox_var"].get()]
        if selected_accounts:
            newfeedhandle(selected_accounts)
            redirect('post_page_list')
            return
            # fetch_and_display_accounts()
            # update_process_count()
        else:
            print("Bạn đã không chọn tài khoản.")

    def update_process_count():
        process_count = len(post_process_instance.get_all_processes())
        process_button.config(text=f"Danh sách tiến trình ({process_count})")

    submit_button = ttk.Button(frame, text="Xác nhận", style="Custom.TButton", command=submit_selection)
    submit_button.pack(fill=tk.X, pady=5, expand=True)

    process_button = ttk.Button(frame, text=f"Danh sách tiến trình ({len(post_process_instance.get_all_processes())})", 
                                style="Custom.TButton", command=lambda: redirect('post_page_list'))
    process_button.pack(fill=tk.X, pady=5, expand=True)


    # Nút quay lại
    back_button = ttk.Button(frame, text="Quay lại", style="Custom.TButton", command=lambda: redirect('home'))
    back_button.pack(fill=tk.X, pady=5, expand=True)

    return frame


def close_process(account):
    post_process_instance.stop_process(account.get('id'))

def post_page_list():
    root = get_root()
    from helpers.base import redirect
    accounts = post_process_instance.get_all_processes()  # Lấy tất cả tiến trình đang chạy từ instance
    
    frame = ttk.Frame(root, padding="10", style="Custom.TFrame")
    frame.grid(row=0, column=0, sticky="nsew")

    # Thêm label để hiển thị số lượng tiến trình
    total_process_label = tk.Label(frame, text=f"Số tài khoản đang chạy: {len(accounts)}", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
    total_process_label.pack(pady=10)

    # Hiển thị danh sách các tài khoản dưới dạng bảng
    if len(accounts) > 0:
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)

        # Tạo bảng với các thẻ <tr> và <td>
        table = tk.Frame(table_frame)
        table.pack(fill="x", padx=20, pady=5)

        # Tạo header bảng
        header = tk.Frame(table)
        header.pack(fill="x", pady=5)

        header_label1 = tk.Label(header, text="Tài khoản", font=("Segoe UI", 12, 'bold'), width=25)
        header_label1.pack(side="left", padx=5)

        header_label1 = tk.Label(header, text="Tổng số tiến trình", font=("Segoe UI", 12, 'bold'), width=25)
        header_label1.pack(side="left", padx=5)

        header_label2 = tk.Label(header, text="Trạng thái", font=("Segoe UI", 12, 'bold'), width=25)
        header_label2.pack(side="left", padx=5)

        header_label3 = tk.Label(header, text="Hành động", font=("Segoe UI", 12, 'bold'), width=15)
        header_label3.pack(side="right", padx=5)

        # Hiển thị các tiến trình
        for account_id, account in accounts.items():
            row = tk.Frame(table)
            row.pack(fill="x", pady=5)

            account_label = tk.Label(row, text=account["name"], font=("Segoe UI", 12), width=25)
            account_label.pack(side="left", padx=5)

            task_label = tk.Label(row, text=len(account.get('tasks')), font=("Segoe UI", 12), width=25)
            task_label.pack(side="left", padx=5)

            status_label = tk.Label(row, text="Đang xử lý", font=("Segoe UI", 12), width=25)
            status_label.pack(side="left", padx=5)

            account['status_label'] = status_label
            account['task_label'] = task_label
            account['row'] = row
            
            if account.get('status_process') == 1:
                close_button = ttk.Button(row, text="Đóng", style="Custom.TButton", command=lambda account=account: close_process(account,))
            else:
                close_button = ttk.Button(row, text="Đang đóng...",state="disabled", style="Custom.TButton", command=lambda account=account: close_process(account,))
            close_button.pack(side="right", padx=5)
            account['close_button'] = close_button


        table.update_idletasks()
    else:
        no_process_label = tk.Label(frame, text="Không có tiến trình nào đang chạy.", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
        no_process_label.pack(pady=20)

    # Thêm mới và quay lại
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)

    add_button = ttk.Button(button_frame, text="Thêm mới", style="Custom.TButton", command=lambda: redirect('post'))
    add_button.pack(side="left", padx=5, expand=True)

    back_button = ttk.Button(button_frame, text="Quay lại", style="Custom.TButton", command=lambda: redirect('home'))
    back_button.pack(side="right", padx=5, expand=True)

    return frame

