import tkinter as tk
from tkinter import ttk
from main.root import get_frame
from sql.accounts import Account
from main.newsfeed import get_newsfeed_process_instance
from tools.facebooks.browser_newsfeed import process_newsfeed
import threading
import logging

newsfeed_process_instance = get_newsfeed_process_instance()

def newfeedhandle(selected_accounts):
    try:
        for account in selected_accounts:
            stop_event = threading.Event()
            thread = threading.Thread(target=process_newsfeed, args=(account, stop_event))
            thread.start()
            account['tasks'] = [thread]
            account['stop_event'] = stop_event
            account['status'] = 'Sẵn sàng cào'
            account['status_process'] = 1 # 1: Hoạt động, 2: Đã đóng
            account['status_vie'] = 1 # 1: Cào, 2: Đã đóng
            newsfeed_process_instance.add_process(account)
    except Exception as e:
        logging.error(f"Lỗi không mong muốn: {e}")
        print(f"Lỗi không mong muốn: {e}")

def newsfeed_page():
    account_sql = Account()
    frame = get_frame()
    from helpers.base import render
    label = tk.Label(frame, text="Thêm tài khoản cào newsfeed", font=("Segoe UI", 20), bg="#f0f2f5")
    label.pack(pady=20)
    account_selected = newsfeed_process_instance.get_all_processes()

    # Hàm lấy danh sách tài khoản từ API và hiển thị
    def fetch_and_display_accounts(search_keyword=None):
        params = {'typenot': 2}
        if search_keyword:
            params['name'] = search_keyword
        accounts = account_sql.get_accounts(params)['data']


        # Xóa tất cả các checkbox hiện tại
        for widget in checkbutton_frame.winfo_children():
            widget.destroy()

        row = 0 
        column = 0
        max_name_length = 40
        for account in accounts:
            if account.get('id') in account_selected:
                continue
            var = tk.BooleanVar()
            display_name = account["name"] if len(account["name"]) <= max_name_length else account["name"][:max_name_length] + "..."
            cb = ttk.Checkbutton(checkbutton_frame, text=display_name, variable=var, style="Custom.TCheckbutton")
            cb.grid(row=row, column=column, padx=10, pady=5, sticky="w")
            checkboxes[account["id"]] = {"checkbox_var": var, "account_data": account}
            column += 1
            if column == 5:
                column = 0
                row += 1
            

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
    search_frame.pack(fill=tk.X, pady=5,anchor='center')

    search_entry = ttk.Entry(search_frame, textvariable=search_var,style="Custom.TEntry")
    search_entry.pack(side=tk.LEFT, padx=5, ipady=3, ipadx=5)
    
    search_button = ttk.Button(search_frame, text="Tìm kiếm", style="Custom.TButton", command=search_accounts)
    search_button.pack(side=tk.LEFT, padx=5)

    # Nút xác nhận
    def submit_selection():
        selected_accounts = [data["account_data"] for account_id, data in checkboxes.items() if data["checkbox_var"].get()]
        if selected_accounts:
            newfeedhandle(selected_accounts)
            render('newsfeed_page_list')
            return

    button_frame = tk.Frame(frame, bg="#f0f2f5")
    button_frame.pack(pady=10)

    submit_button = ttk.Button(button_frame, text="Xác nhận", style="Custom.TButton", command=submit_selection)
    submit_button.pack(side=tk.LEFT,fill=tk.X, pady=5, expand=True)

    process_button = ttk.Button(button_frame, text=f"Danh sách tiến trình ({len(newsfeed_process_instance.get_all_processes())})", 
                                style="Custom.TButton", command=lambda: render('newsfeed_page_list'))
    process_button.pack(side=tk.LEFT,fill=tk.X, pady=5, expand=True)


    # Nút quay lại
    back_button = ttk.Button(button_frame, text="Quay lại", style="Custom.TButton", command=lambda: render('home'))
    back_button.pack(side=tk.LEFT,fill=tk.X, pady=5, expand=True)


def close_process(account):
    newsfeed_process_instance.stop_process(account.get('id'))

def newsfeed_page_list():
    frame = get_frame()
    from helpers.base import render
    label = tk.Label(frame, text="Danh sách tài khoản cào newsfeed", font=("Segoe UI", 20), bg="#f0f2f5")
    label.pack(pady=20)
    accounts = newsfeed_process_instance.get_all_processes()  # Lấy tất cả tiến trình đang chạy từ instance

    # Thêm label để hiển thị số lượng tiến trình
    total_process_label = tk.Label(frame, text=f"Số tài khoản đang chạy: {len(accounts)}", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
    total_process_label.pack(pady=10)

    # Hiển thị danh sách các tài khoản dưới dạng bảng
    if len(accounts) > 0:
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(table_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        
        table_inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=table_inner_frame, anchor="nw")

        # Đặt kích thước nội dung và kích hoạt cuộn khi cần
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        table_inner_frame.bind("<Configure>", on_frame_configure)

        header = ttk.Frame(table_inner_frame)
        header.pack(fill="x", pady=5)
        ttk.Label(header, text="Tài khoản", font=("Segoe UI", 12, 'bold'), width=25).pack(side="left", padx=5)
        ttk.Label(header, text="Tổng số tiến trình", font=("Segoe UI", 12, 'bold'), width=25).pack(side="left", padx=5)
        ttk.Label(header, text="Trạng thái", font=("Segoe UI", 12, 'bold'), width=25).pack(side="left", padx=5)
        ttk.Label(header, text="Hành động", font=("Segoe UI", 12, 'bold'), width=15).pack(side="right", padx=5)


        # Hiển thị các tiến trình
        for account_id, account in accounts.items():
            row = ttk.Frame(table_inner_frame)
            row.pack(fill="x", pady=5)

            account_label = ttk.Label(row, text=account["name"], font=("Segoe UI", 12), width=25).pack(side="left", padx=5)
            task_label = ttk.Label(row, text=len(account.get('tasks')), font=("Segoe UI", 12), width=25)
            task_label.pack(side="left", padx=5)
            account['task_label'] = task_label

            status_label = ttk.Label(row, text=account.get("status"), font=("Segoe UI", 12), width=25)
            status_label.pack(side="left", padx=5)
            account['status_label'] = status_label

            account['row'] = row
            
            if account.get('status_process') == 1:
                close_button = ttk.Button(row, text="Đóng", style="Custom.TButton", command=lambda account=account: close_process(account,))
            else:
                close_button = ttk.Button(row, text="Đang đóng...", state="disabled", style="Custom.TButton", command=lambda account=account: close_process(account,))
            close_button.pack(side="right", padx=5)

            account['close_button'] = close_button

            vie_button = ttk.Button(
                row,
                text="Bật cào vie" if account.get('status_vie') == 1 else "Tắt cào vie",
                style="Custom.TButton",
                command=lambda account=account: newsfeed_process_instance.update_statusVie(account,)
            )
            vie_button.pack(side="right", padx=5)
            account['vie_button'] = vie_button

            accounts = newsfeed_process_instance.get_all_processes()  # Kiểm tra kiểu dữ liệu trả về

        table_inner_frame.update_idletasks()
    else:
        no_process_label = tk.Label(frame, text="Không có tiến trình nào đang chạy.", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
        no_process_label.pack(pady=20)

    # Thêm mới và quay lại
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, pady=10)

    add_button = ttk.Button(button_frame, text="Thêm mới", style="Custom.TButton", command=lambda: render('newsfeed'))
    add_button.pack(side="left", padx=5, expand=True)

    back_button = ttk.Button(button_frame, text="Quay lại", style="Custom.TButton", command=lambda: render('home'))
    back_button.pack(side="right", padx=5, expand=True)

    return frame

