from router import router
from tkinter import messagebox
import json

def redirect(page_name):
    frame = router.get(page_name)()
    if 'logs' in page_name: return
    if frame is None:
        raise ValueError(f"Frame '{page_name}' không được khởi tạo.")
    frame.tkraise()


def config(key=None):
    try:
        # Mở file config.json và đọc dữ liệu
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)

        # Nếu không truyền key, trả về tất cả cấu hình
        if key is None:
            return config_data

        # Nếu có key, trả về giá trị tương ứng với key đó
        if key in config_data:
            return config_data[key]
        else:
            messagebox.showwarning("Cảnh báo", f"Key '{key}' không tồn tại trong cấu hình.")
            return None

    except FileNotFoundError:
        config_data = {
            "browser": "chrome",
            "headless": True,
            "driver_path": ""
        }
        with open("config.json", "w") as config_file:
            json.dump(config_data, config_file, indent=4)
        messagebox.showinfo("Thông báo", "File cấu hình đã được tạo với cấu hình mặc định.")
        if key is None:
            return config_data
        if key in config_data:
            return config_data[key]
        else:
            messagebox.showwarning("Cảnh báo", f"Key '{key}' không tồn tại trong cấu hình.")
            return None
    except json.JSONDecodeError:
        messagebox.showerror("Lỗi", "File cấu hình không hợp lệ.")
        return None
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi đọc file cấu hình: {str(e)}")
        return None