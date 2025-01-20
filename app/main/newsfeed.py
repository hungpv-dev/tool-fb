import threading
import json
class NewsFeedProcess:
    def __init__(self):
        self.progress_data = {}

    def add_process(self, process):
        self.progress_data[process["id"]] = process

    def update_process(self, id, new_text):
        try:
            if id in self.progress_data:
                process = self.progress_data[id]
                status_label = process.get("status_label") 
                process["status"] = new_text
                if status_label:
                    status_label.config(text=new_text) 
        except Exception as e:
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
        
    def update_task(self, id, newtask):
        try:
            if id in self.progress_data:
                process = self.progress_data[id]
                process.get('tasks').append(newtask)
                task_label = process.get("task_label") 
                if task_label:
                    task_label.config(text=len(process.get('tasks')))
        except Exception as e:
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")

    def update_statusVie(self,acc):
        try:
            status_vie = acc.get('status_vie')
            process = self.progress_data[acc.get('id')]
            if status_vie == 1:
                if 'vie_button' in process:
                    process['vie_button'].config(text="Tắt cào vie")
                process['status_vie'] = 2
            else:
                if 'vie_button' in process:
                    process['vie_button'].config(text="Bật cào vie")
                process['status_vie'] = 1
        except Exception as e:
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")

    def show(self, id):
        process = self.progress_data[id]
        return process


    def stop_process(self, id):
        # Dừng tiến trình theo id
        try:
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

                # Chạy stop_task trong một thread riêng biệt
                threading.Thread(target=stop_task, args=(process,), daemon=True).start()
        except Exception as e:
            # logging.error(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")
            print(f"Đã xảy ra lỗi khi cập nhật task_label: {e}")

    def get_all_processes(self):
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
newsfeed_process = NewsFeedProcess()

def get_newsfeed_process_instance():
    return newsfeed_process
