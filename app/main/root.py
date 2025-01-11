import tkinter as tk

root_instance = None

def create_app():
    root = tk.Tk()
    root.title("Ứng dụng Quản lý")
    # root.geometry("400x500")  # Tăng chiều cao cửa sổ
    root.config(bg="#f0f2f5")  # Màu nền của Facebook (#f0f2f5)
    return root

def get_root(init=False):
    global root_instance 
    
    # Nếu root chưa được khởi tạo, tạo mới
    if root_instance is None:
        root_instance = create_app()
    
    return root_instance