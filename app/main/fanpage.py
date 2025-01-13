import tkinter as tk
from tkinter import ttk
import threading
from time import sleep
import uuid 

class FanpageProcess:
    def __init__(self):
        self.progress_data = {}  # Danh sách lưu trạng thái tiến trình
        self.main_layout = None  # Danh sách lưu trạng thái tiến trình

    def setMainLayout(self,mainLayout):
        self.main_layout = mainLayout

    def add_process(self,id, data, progress_list):
        self.progress_data[id] = data

        process_frame = ttk.Frame(progress_list)
        process_frame.pack(fill="x", padx=20, pady=5)

        progress_label = tk.Label(process_frame, text="Sẵn sàng chạy...", font=("Segoe UI", 12))
        progress_label.pack(side="left", padx=5)

        close_button = ttk.Button(process_frame, text="Đóng", command=lambda id=id: self.stop_process(id,))
        close_button.pack(side="right", padx=5)

        # Liên kết giao diện với tiến trình
        data["frame"] = process_frame
        data["label"] = progress_label
        data["close_button"] = close_button

        progress_list.update_idletasks()


    def update_process(self, id, new_text):
        if id in self.progress_data:
            process = self.progress_data[id]
            label = process.get("label") 
            if label:
                label.config(text=new_text) 
            process["status_show"] = new_text

    def stop_process(self, id):
        if id in self.progress_data:
            process = self.progress_data[id]
            process['status_process'] = 2
            stop_event = process.get('stop_event')

            if stop_event:
                stop_event.set()

            close_button = process.get("close_button")
            if close_button:
                close_button.config(text="Đang đóng...", state="disabled")
        
        def stop_task(process):
            threa = process.get('thread')
            threa.join() 

            self.progress_data[id].get('frame').destroy()
            del self.progress_data[id]

            # Chạy stop_task trong một thread riêng biệt
        threading.Thread(target=stop_task, args=(process,), daemon=True).start()


    def get_all_processes(self):
        # Trả về danh sách tiến trình đang chạy
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
fanpage_process = FanpageProcess()

def get_fanpage_process_instance():
    return fanpage_process