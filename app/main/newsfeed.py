class NewsFeedProcess:
    def __init__(self):
        self.progress_data = [] 

    def add_process(self, process):
        # Thêm tiến trình vào danh sách
        self.progress_data.append(process)

    def update_process(self, id, new_text):
        # Cập nhật tiến trình theo id
        for process in self.progress_data:
            if process.get("id") == id:
                process["status"] = new_text  # Thêm một trường 'status' nếu muốn
                break

    def stop_process(self, id):
        # Dừng tiến trình theo id
        for process in self.progress_data:
            if process.get('id') == id:
                process['stop_event'].set()  # Đặt sự kiện dừng
                self.progress_data.remove(process)  # Xóa tiến trình khỏi danh sách
                break

    def get_all_processes(self):
        return self.progress_data


# Biến toàn cục lưu instance của FanpageProcess
newsfeed_process = NewsFeedProcess()

def get_newsfeed_process_instance():
    return newsfeed_process
