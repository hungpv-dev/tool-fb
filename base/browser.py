from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import logging
import os

class Browser:
    def __init__(self,account = '/hung',dirextension = None):
        self.account = account
        self.dirextension = dirextension
        base_profile_dir = "/profiles"+account

        if not os.path.exists(base_profile_dir):
            os.makedirs(base_profile_dir)

        self.profile_dir = base_profile_dir
        
        
    def start(self, headless=True):
        chrome_options = Options()
        
        if self.profile_dir != '/profiles/crawl':
            chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")

        if self.dirextension: 
            chrome_options.add_extension(self.dirextension)

        # Tắt WebGPU và các tính năng GPU
        chrome_options.add_argument("--disable-webgpu")  # Tắt WebGPU
        chrome_options.add_argument("--disable-gpu")  # Tắt GPU
        chrome_options.add_argument("--disable-software-rasterizer")  # Tắt phần mềm vẽ đồ họa
        chrome_options.add_argument("--disable-accelerated-2d-canvas")  # Tắt tăng tốc vẽ canvas 2D
        chrome_options.add_argument("--disable-gpu-compositing")  # Tắt GPU compositing
        chrome_options.add_argument("--disable-dev-shm-usage")  # Tắt việc sử dụng /dev/shm

        # Tùy chọn chạy headless (nếu cần)
        if headless: 
            chrome_options.add_argument("--headless")  # Chế độ không giao diện
            chrome_options.add_argument("--no-sandbox")  # Không sử dụng sandbox

        # Tối ưu tình huống cụ thể
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo
        chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn popup
        chrome_options.add_argument("--disable-translate")  # Tắt dịch trang
        chrome_options.add_argument("--disable-infobars")  # Tắt thanh thông tin của Chrome
        chrome_options.add_argument("--disable-browser-side-navigation")  # Tắt tối ưu điều hướng

        # Vô hiệu hóa proxy
        chrome_options.add_argument("--no-proxy-server")
        chrome_options.add_argument("--proxy-server='direct://'")
        chrome_options.add_argument("--proxy-bypass-list=*")

        # Khởi động trình duyệt với các tùy chọn đã cấu hình
        try:
            # Giả sử bạn có phương thức để khởi động trình duyệt
            self.driver = self.start_browser(chrome_options)
            logging.info("Trình duyệt đã khởi động thành công")
            return self.driver
        except Exception as e:
            logging.error(f"Lỗi khi khởi động trình duyệt: {e}")

    def start_browser(self, chrome_options):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def cleanup(self):
        """Xóa thư mục tạm nếu được tạo."""
        if hasattr(self, 'profile_dir') and self.profile_dir:
            import shutil
            shutil.rmtree(self.profile_dir, ignore_errors=True)
