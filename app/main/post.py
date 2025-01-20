import threading
import logging
class PostProcess:
    def __init__(self):
        self.progress_data = {}

    def add_process(self, process):
        self.progress_data[process["id"]] = process

    def update_process(self, id, new_text):
        try:
            if id in self.progress_data:
                process = self.progress_data[id]
                process["status"] = new_text
                status_label = process.get("status_label") 
                if status_label:
                    status_label.config(text=new_text) 
        except Exception as e:
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
        
    def update_task(self, id, newtask):
        try:
            if id in self.progress_data:
                process = self.progress_data[id]
                process.get('tasks').append(newtask)
                task_label = process.get("task_label") 
                if task_label:
                    task_label.config(text=len(process.get('tasks')))
        except Exception as e:
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")

        
    def stop_process(self, id):
        try:
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
                def stop_task(process):
                    tasks = process.get('tasks', [])
                    for thread in tasks:
                        if thread.is_alive():
                            thread.join()  # Đợi các thread kết thúc

                    # Sau khi hoàn thành, xóa tiến trình khỏi danh sách và đóng giao diện
                    self.progress_data[id].get('row').destroy()
                    del self.progress_data[id]  # Xóa khỏi progress_data

            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
                # Chạy stop_task trong một thread riêng biệt
                threading.Thread(target=stop_task, args=(process,), daemon=True).start()
        except Exception as e:
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")

    def get_all_processes(self):
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
post_process = PostProcess()

def get_post_process_instance():
    return post_process
