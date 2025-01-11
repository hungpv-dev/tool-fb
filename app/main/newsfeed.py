import threading
class NewsFeedProcess:
    def __init__(self):
        self.progress_data = {}

    def add_process(self, process):
        self.progress_data[process["id"]] = process

    def update_process(self, id, new_text):
        if id in self.progress_data:
            process = self.progress_data[id]
            status_label = process.get("status_label") 
            if status_label:
                status_label.config(text=new_text) 
            process["status"] = new_text
        
    def update_task(self, id, newtask):
        if id in self.progress_data:
            process = self.progress_data[id]
            process.get('tasks').append(newtask)
            task_label = process.get("task_label") 
            if task_label:
                task_label.config(text=len(process.get('tasks')))
        
    def stop_process(self, id, process_frame):
        # Dừng tiến trình theo id
        if id in self.progress_data:
            process = self.progress_data[id]
            process['status_process'] = 2
            stop_event = process.get('stop_event')
            
            # Đặt stop_event nếu có
            if stop_event:
                stop_event.set()

            # Cập nhật giao diện ngay lập tức
            close_button = process.get("close_button")
            if close_button:
                close_button.config(text="Đang đóng...", state="disabled")

            # Định nghĩa task dừng tiến trình trong một thread riêng
            def stop_task(process, process_frame):
                tasks = process.get('tasks', [])
                for thread in tasks:
                    if thread.is_alive():
                        thread.join()  # Đợi các thread kết thúc

                # Sau khi hoàn thành, xóa tiến trình khỏi danh sách và đóng giao diện
                del self.progress_data[id]  # Xóa khỏi progress_data
                process_frame.destroy()  # Đóng frame

            # Chạy stop_task trong một thread riêng biệt
            threading.Thread(target=stop_task, args=(process, process_frame), daemon=True).start()

    def get_all_processes(self):
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
newsfeed_process = NewsFeedProcess()

def get_newsfeed_process_instance():
    return newsfeed_process
