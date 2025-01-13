from helpers.base import redirect
from main.root import get_root

def create_facebook_like_interface():
    root = get_root(True)

    # Lúc đầu, hiển thị trang chính (main_frame)
    redirect('home')

    # Chạy vòng lặp chính của giao diện
    root.mainloop()

if __name__ == "__main__":
# Gọi hàm để tạo giao diện đẹp
    create_facebook_like_interface()