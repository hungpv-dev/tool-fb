import tkinter as tk
from tkinter import ttk
from crawl import crawl
import threading
running_browsers = 0
def submit_page_count(page_input_entry, show_frame, main_frame):
    countPage = page_input_entry.get()
    try:
        countPage = int(countPage)
        if countPage < 1:
            raise ValueError("Số lượng phải lớn hơn hoặc bằng 1.")
        print(f"Bắt đầu cào {countPage} Fanpage.")
        # Chạy crawl trong một thread riêng biệt
        crawl_thread = threading.Thread(target=crawl, args=(countPage,))
        crawl_thread.start()
        
        show_frame(main_frame)  # Quay lại trang chính
    except ValueError as e:
        print(f"Giá trị không hợp lệ: {e}")


def create_page_input_frame(root, show_frame, main_frame):
    # Tạo frame cho trang nhập số lượng Fanpage
    page_input_frame = ttk.Frame(root, padding="10", style="Custom.TFrame")
    page_input_frame.grid(row=0, column=0, sticky="nsew")
    
    # Thêm Label và Entry vào trang nhập số lượng Fanpage
    label2 = tk.Label(page_input_frame, text="Nhập số lượng Fanpage muốn lấy:", font=("Segoe UI", 14), bg="#f0f2f5", fg="#1c1e21")
    label2.pack(pady=20)

    page_input_entry = ttk.Entry(page_input_frame, font=("Segoe UI", 12), width=20)
    page_input_entry.pack(pady=10)

    submit_button = ttk.Button(page_input_frame, text="Xác nhận", style="Custom.TButton", command=lambda: submit_page_count(page_input_entry, show_frame, main_frame))
    submit_button.pack(fill=tk.X, pady=5, expand=True)

    back_button = ttk.Button(page_input_frame, text="Quay lại", style="Custom.TButton", command=lambda: show_frame(main_frame))
    back_button.pack(fill=tk.X, pady=5, expand=True)

    return page_input_frame, page_input_entry
