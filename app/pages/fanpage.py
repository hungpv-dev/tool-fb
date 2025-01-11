import tkinter as tk
from tkinter import ttk
from main.root import get_root
from tools.facebooks.get_post_from_fanpage import process_crawl
from main.fanpage import get_fanpage_process_instance
import threading
from time import sleep
import uuid

fanpage_process_instance = get_fanpage_process_instance()

def submit_page_count(page_input_entry, progress_list):
    from helpers.base import redirect
    countPage = page_input_entry.get()
    try:
        countPage = int(countPage)
        if countPage < 1:
            raise ValueError("Số lượng phải lớn hơn hoặc bằng 1.")
        print(f"Bắt đầu cào {countPage} Fanpage.")
        
        # Thêm tất cả các tiến trình vào danh sách và cập nhật giao diện
        for count in range(countPage):
            id = uuid.uuid4()
            stop_event = threading.Event()  
            thread = threading.Thread(target=process_crawl, args=(id, stop_event))
            thread.start()

            # Thêm tiến trình vào danh sách và cập nhật giao diện
            fanpage_process_instance.add_process(id,progress_list,stop_event)
            sleep(1)
        
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    except ValueError as e:
        print(f"Giá trị không hợp lệ: {e}")

def fanpage_page():
    root = get_root()
    from helpers.base import redirect
    frame = ttk.Frame(root, padding="10", style="Custom.TFrame")
    frame.grid(row=0, column=0, sticky="nsew")

    # Thêm label để hiển thị số lượng tiến trình
    total_process_label = tk.Label(frame, text=f"Số tab đang mở: 0", font=("Segoe UI", 12), bg="#f0f2f5", fg="#1c1e21")
    total_process_label.pack(pady=10)

    label2 = tk.Label(frame, text="Số tab muốn mở:", font=("Segoe UI", 14), bg="#f0f2f5", fg="#1c1e21")
    label2.pack(pady=20)

    page_input_entry = ttk.Entry(frame, font=("Segoe UI", 12), width=20)
    page_input_entry.pack(pady=10)

    submit_button = ttk.Button(frame, text="Xác nhận", style="Custom.TButton", command=lambda: submit_page_count(page_input_entry, progress_list))
    submit_button.pack(fill=tk.X, pady=5, expand=True)

    back_button = ttk.Button(frame, text="Quay lại", style="Custom.TButton", command=lambda: redirect('home'))
    back_button.pack(fill=tk.X, pady=5, expand=True)

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

    for process in all_processes:
        process_frame = ttk.Frame(progress_list)
        process_frame.pack(fill="x", padx=20, pady=5)
        progress_label = tk.Label(process_frame, text=f"Đang xử lý...", font=("Segoe UI", 12))
        progress_label.pack(side="left", padx=5)
        close_button = ttk.Button(process_frame, text="Đóng")
        close_button.pack(side="right", padx=5)
        
        
        process["frame"] =  process_frame
        process["label"] =  progress_label
        process["button"] =  close_button
        

        id = process.get('id')
        # Sửa lại cách gọi lambda để truyền đúng giá trị id tại thời điểm này
        close_button.config(command=lambda id=id, progress_list=progress_list: fanpage_process_instance.stop_process(id, progress_list))
        
        progress_list.update_idletasks()

    return frame

