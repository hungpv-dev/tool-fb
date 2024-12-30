from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tempfile
import os

class Browser:
    def __init__(self,account = 'hung',dirextension = None):
        self.account = account
        self.dirextension = dirextension
        if account != 'hung':
            base_temp_dir = tempfile.gettempdir()
            profile_dir = os.path.join(base_temp_dir, f"account_{account}")
            if not os.path.exists(profile_dir):
                os.makedirs(profile_dir)
            self.profile_dir = profile_dir
        
        
    def start(self, headless = True):
        chrome_options = Options()
        if self.account != 'hung':
            chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        if self.dirextension is not None: 
            chrome_options.add_extension(self.dirextension)
        
        # Tùy chọn chạy headless (nếu cần)
        if headless: 
            chrome_options.add_argument("--headless")  # Chế độ không giao diện
            chrome_options.add_argument("--disable-gpu")  # Vô hiệu hóa GPU
            chrome_options.add_argument("--no-sandbox")  # Không sử dụng sandbox
            chrome_options.add_argument("--disable-software-rasterizer")  # Tắt phần mềm rasterizer
            chrome_options.add_argument("--use-gl=swiftshader")  # Sử dụng renderer SwiftShader
            chrome_options.add_argument("--disable-dev-shm-usage")  # Giúp tránh một số lỗi liên quan đến bộ nhớ
            # chrome_options.add_argument("--remote-debugging-port=9222")  # Mở cổng debug cho Chrome


        # Các tùy chọn khác
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo
        chrome_options.add_argument("--disable-geolocation")  # Tắt định vị
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Giả lập UI cho media
        chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn popup

        # chrome_options.add_argument("--incognito")  # Chế độ ẩn danh`

        # Tùy chọn thêm để xử lý lỗi về GPU và virtualization
        chrome_options.add_argument("--disable-extensions")  # Tắt các tiện ích mở rộng không cần thiết
        chrome_options.add_argument("--disable-accelerated-2d-canvas")  # Vô hiệu hóa tăng tốc canvas 2D
        chrome_options.add_argument("--disable-accelerated-video-decode")  # Vô hiệu hóa tăng tốc video
        chrome_options.add_argument("--disable-accelerated-mjpeg-decode")  # Vô hiệu hóa tăng tốc MJPEG

        service = Service('chromedriver.exe') 
        browser = webdriver.Chrome(service=service,options=chrome_options)
        
        return browser
    
    def cleanup(self):
        """Xóa thư mục tạm nếu được tạo."""
        if hasattr(self, 'profile_dir') and self.profile_dir:
            import shutil
            shutil.rmtree(self.profile_dir, ignore_errors=True)
