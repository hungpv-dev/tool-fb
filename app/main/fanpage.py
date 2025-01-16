import tkinter as tk
from tkinter import ttk
import threading
import logging
from time import sleep
import uuid 

class FanpageProcess:
    def __init__(self):
        self.progress_data = {}  # Danh sách lưu trạng thái tiến trình
        self.progress_list = None  # Danh sách lưu trạng thái tiến trình

    def setMainLayout(self,progress_list):
        self.progress_list = progress_list

    def add_process(self,id, data):
        self.progress_data[id] = data
        self.insert_view(id)

    def insert_view(self,id):
        if id in self.progress_data:
            process = self.progress_data[id]
            process_frame = ttk.Frame(self.progress_list)
            process_frame.pack(fill="x", padx=20, pady=5)

            progress_label = tk.Label(process_frame, text=process["status_show"], font=("Segoe UI", 12))
            progress_label.pack(side="left", padx=5)
            
            if process.get('status_process') == 1:
                close_button = ttk.Button(process_frame, text="Đóng")
            else:
                close_button = ttk.Button(process_frame, text="Đang đóng...",state="disabled")
            close_button.pack(side="right", padx=5)
            
            process["frame"] =  process_frame
            process["label"] =  progress_label
            process["close_button"] =  close_button

            # Sửa lại cách gọi lambda để truyền đúng giá trị id tại thời điểm này
            close_button.config(command=lambda id=id: self.stop_process(id, ))

            self.progress_list.update_idletasks()


    def update_process(self, id, new_text):
        try:
            if id in self.progress_data:
                process = self.progress_data[id]
                label = process.get("label") 
                if label:
                    # Đảm bảo rằng việc cập nhật label diễn ra trong main thread
                    label.after(0, lambda: label.config(text=new_text))  # Thực hiện cập nhật trong main thread
                    process["status_show"] = new_text
        except Exception as e:
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
        

    def stop_process(self, id):
        try:
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
        except Exception as e:
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")


    def get_all_processes(self):
        # Trả về danh sách tiến trình đang chạy
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
fanpage_process = FanpageProcess()

def get_fanpage_process_instance():
    return fanpage_process