import tkinter as tk
from tkinter import ttk
from tools.facebooks.get_post_from_fanpage import process_crawl
from main.fanpage import get_fanpage_process_instance
import threading
from time import sleep
import uuid
import logging
from main.root import get_frame
from tkinter import messagebox

fanpage_process_instance = get_fanpage_process_instance()

def submit_page_count(page_input_entry,total_process_label):
    countPage = page_input_entry.get()
    try:
        countPage = int(countPage)
        if countPage < 1:
            messagebox.showwarning("Cảnh báo","Số lượng phải lớn hơn hoặc bằng 1.")
        logging.info(f"Bắt đầu cào {countPage} Fanpage.")
        print(f"Bắt đầu cào {countPage} Fanpage.")

        def update_process_count():
            total_process_label.config(text=f"Số tab đang mở: {len(fanpage_process_instance.get_all_processes())}")

        for count in range(countPage):
            id = uuid.uuid4()
            stop_event = threading.Event()
            thread = threading.Thread(target=process_crawl,args=(id,stop_event))
            thread.start()
            data = {
                'stop_event': stop_event,
                'thread': thread,
                'status_show': 'Sẵn sàng chạy...',
                'status_process': 1,  # 1: Hoạt động, 2: Đã đóng
            }
            fanpage_process_instance.add_process(id, data)
            update_process_count()
            sleep(1) 

    except Exception as e:
        logging.error(f"Lỗi không mong muốn: {e}")
        print(f"Lỗi không mong muốn: {e}")
    except ValueError as e:
        logging.error(f"Giá trị không hợp lệ: {e}")
        print(f"Giá trị không hợp lệ: {e}")


def fanpage_page():
    frame = get_frame()
    """Hiển thị nội dung trang Home."""
    label = tk.Label(frame, text="Trang chủ", font=("Segoe UI", 20), bg="#f0f2f5")
    label.pack(pady=20)
    
    from helpers.base import render
    
    # Thêm label để hiển thị số lượng tiến trình
    total_process_label = tk.Label(frame, text=f"Số tab đang mở: 0", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
    total_process_label.pack(pady=10)

    label2 = tk.Label(frame, text="Số tab muốn mở:", font=("Segoe UI", 14), bg="#f0f2f5", fg="#1c1e21")
    label2.pack(pady=20)

    page_input_entry = ttk.Entry(frame, font=("Segoe UI", 12), width=20)
    page_input_entry.pack(pady=10)

    button_frame = tk.Frame(frame, bg="#f0f2f5")
    button_frame.pack(pady=10)

    submit_button = ttk.Button(button_frame,width=15, text="Xác nhận", style="Custom.TButton", command=lambda: submit_page_count(page_input_entry,total_process_label))
    submit_button.pack(side=tk.LEFT,fill=tk.X, pady=5, expand=True)

    back_button = ttk.Button(button_frame,width=15, text="Quay lại", style="Custom.TButton", command=lambda: render('home'))
    back_button.pack(side=tk.LEFT,fill=tk.X, pady=5, expand=True)


    canvas = tk.Canvas(frame)
    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scroll_y.set)

    scroll_y.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    progress_list = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=progress_list, anchor="nw")

    def update_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    progress_list.bind("<Configure>", update_scroll_region)

    # Hiển thị tất cả tiến trình cũ nếu có
    all_processes = fanpage_process_instance.get_all_processes()
    
    # Cập nhật label với tổng số tiến trình
    total_process_label.config(text=f"Số tab đang mở: {len(all_processes)}")

    fanpage_process_instance.setMainLayout(progress_list)

    for process_id,process in all_processes.items():
       fanpage_process_instance.insert_view(process_id)

    return frame

