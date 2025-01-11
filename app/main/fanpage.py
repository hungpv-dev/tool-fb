import tkinter as tk
from tkinter import ttk
import threading
from time import sleep
import uuid 

class FanpageProcess:
    def __init__(self):
        self.progress_data = []  # Danh sách lưu trạng thái tiến trình

    def add_process(self,id, progress_list, stop_event):
        # Tạo frame chứa label và button trên cùng một dòng
        process_frame = ttk.Frame(progress_list)
        process_frame.pack(fill="x", padx=20, pady=5)

        progress_label = tk.Label(process_frame, text=f"Cào page", font=("Segoe UI", 12))
        progress_label.pack(side="left", padx=5)

        close_button = ttk.Button(process_frame, text="Đóng")
        close_button.pack(side="right", padx=5)

        self.progress_data.append({
            "id": id,
            "frame": process_frame,
            "label": progress_label,
            "button": close_button,
            "stop_event": stop_event
        })

        # Cấu hình button đóng cho từng tiến trình
        close_button.config(command=lambda: self.stop_process(id,progress_list))
        progress_list.update_idletasks()

    def update_process(self, id, new_text):
        for process in self.progress_data:
            if process.get("id") == id:
                process["label"].config(text=new_text)
                break

    def stop_process(self, id,progress_list):
        for process in self.progress_data:
            if process.get('id') == id:
                process['stop_event'].set()
                process['label'].config(text="Đã dừng")
                process['button'].config(state="disabled")
                process["frame"].destroy()
                self.progress_data.remove(process) 
                progress_list.update_idletasks()
                break


    def get_all_processes(self):
        # Trả về danh sách tiến trình đang chạy
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
fanpage_process = FanpageProcess()

def get_fanpage_process_instance():
    return fanpage_process