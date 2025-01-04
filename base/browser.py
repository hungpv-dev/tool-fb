from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

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
        return self.start_firefox(headless)

        chrome_options = Options()
        
        if self.profile_dir != '/profiles/crawl':
            chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")

        if self.dirextension: 
            chrome_options.add_extension(self.dirextension)

        # Tùy chọn chạy headless (nếu cần)
        if headless: 
            chrome_options.add_argument("--headless=new")  # Chế độ không giao diện, dùng API mới
            chrome_options.add_argument("--no-sandbox")  # Không sử dụng sandbox

        # Vô hiệu hóa GPU và rendering liên quan
        # chrome_options.add_argument("--disable-gpu")  # Tắt GPU
        # chrome_options.add_argument("--disable-software-rendering")  # Tắt rendering phần mềm

        # Các tối ưu khác
        chrome_options.add_argument("--disable-notifications")  # Tắt thông báo
        chrome_options.add_argument("--disable-translate")  # Tắt tính năng dịch
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Tránh bị nhận diện tự động hóa
        chrome_options.add_argument("--disable-infobars")  # Tắt thanh thông báo "Chrome is being controlled..."
        chrome_options.add_argument("--start-maximized")  # Mở rộng cửa sổ
        chrome_options.add_argument("--disable-dev-shm-usage")  # Tránh vấn đề bộ nhớ chia sẻ

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

    def start_firefox(self, headless):
        firefox_options = FirefoxOptions()

        # Thiết lập profile người dùng nếu không phải mặc định
        if self.profile_dir and self.profile_dir != '/profiles/crawl':
            firefox_options.set_preference("browser.download.dir", self.profile_dir)

        # Thêm extension nếu có (Firefox yêu cầu định dạng .xpi)
        if self.dirextension:
            firefox_options.add_extension(self.dirextension)

        # Chế độ headless (tùy chọn)
        if headless:
            firefox_options.add_argument("--headless")

        # Vô hiệu hóa các thông báo và tối ưu
        firefox_options.set_preference("dom.webnotifications.enabled", False)  # Tắt thông báo
        firefox_options.set_preference("intl.accept_languages", "en-US, en")  # Ngôn ngữ mặc định

        # Khởi động trình duyệt
        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            return driver
        except Exception as e:
            logging.error(f"Lỗi khi khởi động trình duyệt: {e}")
            raise e  # Ném lỗi để xử lý ngoài hàm

    
    def cleanup(self):
        """Xóa thư mục tạm nếu được tạo."""
        if hasattr(self, 'profile_dir') and self.profile_dir:
            import shutil
            shutil.rmtree(self.profile_dir, ignore_errors=True)
