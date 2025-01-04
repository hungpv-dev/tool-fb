from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import tempfile
import os

class Browser:
    def __init__(self,account = '/hung',dirextension = None):
        self.account = account
        self.dirextension = dirextension
        base_profile_dir = "/profiles"+account

        if not os.path.exists(base_profile_dir):
            os.makedirs(base_profile_dir)

        self.profile_dir = base_profile_dir
        
        
    def start(self, headless = True):
        chrome_options = Options()
        if self.profile_dir != '/profiles/crawl':
            chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        if self.dirextension: 
            chrome_options.add_extension(self.dirextension)
        
        # Tắt WebGPU
        chrome_options.add_argument("--disable-webgpu")  # Tắt WebGPU

        # Tùy chọn chạy headless (nếu cần)
        if headless: 
            chrome_options.add_argument("--headless")  # Chế độ không giao diện
            chrome_options.add_argument("--no-sandbox")  # Không sử dụng sandbox
            chrome_options.add_argument("--disable-gpu")  # Tắt GPU khi headless

        # Tối ưu tình huống cụ thể
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo
        chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn popup
        chrome_options.add_argument("--disable-translate")  # Tắt dịch trang
        chrome_options.add_argument("--disable-infobars")  # Tắt thanh thông tin của Chrome
        chrome_options.add_argument("--disable-browser-side-navigation")  # Tắt tối ưu điều hướng

        # #  Tăng tốc phần cứng!
        chrome_options.add_argument("--enable-unsafe-swiftshader")  # Cho phép SwiftShader nếu không có GPU

        # Tăng cường bảo mật và tránh bị phát hiện sử dụng Selenium
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service('chromedriver.exe') 
        browser = webdriver.Chrome(service=service,options=chrome_options)
        
        return browser
    
    def cleanup(self):
        """Xóa thư mục tạm nếu được tạo."""
        if hasattr(self, 'profile_dir') and self.profile_dir:
            import shutil
            shutil.rmtree(self.profile_dir, ignore_errors=True)
