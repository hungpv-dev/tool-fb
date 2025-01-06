from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import logging
import os


class Browser:
    def __init__(self, account='/hung', proxy=None, browser_type='chrome'):
        self.account = account
        self.proxy = proxy
        self.browser_type = browser_type  # Chọn loại trình duyệt
        base_profile_dir = "./profiles" + account
        
        if not os.path.exists(base_profile_dir):
            os.makedirs(base_profile_dir, mode=0o755)
        
        os.chmod(base_profile_dir, 0o755)

        self.profile_dir = base_profile_dir

    def start(self, headless=True):
        if self.browser_type == 'chrome':
            return self.start_chrome(headless)
        elif self.browser_type == 'firefox':
            return self.start_firefox(headless)
        elif self.browser_type == 'edge':  # Kiểm tra browser_type
            return self.start_edge(headless)
        else:
            raise ValueError("Unsupported browser type. Please choose 'chrome', 'firefox', or 'edge'.")

    def start_chrome(self, headless):
        chrome_options = Options()
        
        if self.profile_dir != './profiles/crawl':
            full_path = os.path.abspath(self.profile_dir)
            chrome_options.add_argument(f"--user-data-dir={full_path}")
            pass

        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")

        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            seleniumwire_options = {}
            if self.proxy:
                proxy = self.proxy
                seleniumwire_options['proxy'] = {
                    'http': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                    'https': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                    'no_proxy': 'localhost, 127.0.0.1'
                }
            service = Service('chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options,seleniumwire_options=seleniumwire_options)
            return driver
        except Exception as e:
            logging.error(f"Error starting Chrome browser: {e}")
            raise e

    def start_firefox(self, headless):
        firefox_options = FirefoxOptions()
        seleniumwire_options = {}

        # Đảm bảo rằng profile là chính xác để tránh dùng profile mặc định
        if self.profile_dir and self.profile_dir != '/profiles/crawl':
            firefox_options.set_preference("browser.download.dir", self.profile_dir)

        if headless:
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--disable-gpu")  # Giảm tải đồ họa
            firefox_options.add_argument("--no-sandbox")  # Giúp Firefox chạy ổn định trong container hoặc môi trường hạn chế

        # Vô hiệu hóa thông báo push và thay đổi ngôn ngữ
        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("intl.accept_languages", "en-US, en")

        # Tối ưu hóa việc duy trì kết nối lâu dài
        firefox_options.set_preference("network.http.keep-alive", True)  # Duy trì kết nối HTTP để giảm thiểu độ trễ
        firefox_options.set_preference("network.http.max-conns", 100)    # Giới hạn kết nối tối đa
        firefox_options.set_preference("network.http.max-persistent-conns-per-server", 10)

        firefox_options.add_argument("--disable-logging")  # Tắt logging
        firefox_options.add_argument("--disable-dev-shm-usage")  # Sử dụng bộ nhớ ảo thay vì tạo file tạm
        firefox_options.add_argument("--disable-background-networking")  # Tắt background networking
        firefox_options.add_argument("--disable-cache")  # Vô hiệu hóa cache

        # Cấu hình cache (giảm thiểu việc tải lại dữ liệu không cần thiết)
        firefox_options.set_preference("browser.cache.disk.enable", False)
        firefox_options.set_preference("browser.cache.memory.enable", False)

        # Tắt việc lưu lịch sử trình duyệt
        firefox_options.set_preference("places.history.enabled", False)
        firefox_options.set_preference("browser.privatebrowsing.autostart", True)  # Chế độ duyệt riêng tư luôn bật

        try:
            service = FirefoxService(GeckoDriverManager().install())
            # service = FirefoxService('C:\\Users\\ADMIN\\.wdm\\drivers\\geckodriver\\win64\\v0.35.0\\geckodriver.exe')
            if self.proxy:
                proxy = self.proxy
                seleniumwire_options['proxy'] = {
                    'http': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                    'https': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                    'no_proxy': 'localhost, 127.0.0.1'  
                }
            driver = webdriver.Firefox(
                service=service,
                options=firefox_options,
                seleniumwire_options=seleniumwire_options
            )
            # Cấu hình để duy trì session
            driver.set_page_load_timeout(60)  # Thời gian chờ tải trang tối đa
            driver.set_script_timeout(60)     # Thời gian chờ script chạy tối đa

            # Thiết lập xử lý tự động các tình huống lỗi có thể xảy ra (timeout, mất kết nối)
            # driver.implicitly_wait(10)  # Đợi ngầm định tối đa 10s khi truy vấn các phần tử

            return driver
        except Exception as e:
            logging.error(f"Error starting Firefox browser: {e}")
            raise e

    def start_edge(self, headless):
        edge_options = EdgeOptions()

        # Thêm tùy chọn cho profile người dùng nếu cần
        if self.profile_dir != '/profiles/crawl':
            edge_options.add_argument(f"--user-data-dir={self.profile_dir}")


        # Chạy ở chế độ headless nếu cần
        if headless:
            edge_options.add_argument("--headless")
            edge_options.add_argument("--no-sandbox")

        # Thêm các tùy chọn để giảm thiểu thông báo DevTools và lỗi
        edge_options.add_argument("--disable-notifications")
        edge_options.add_argument("--disable-translate")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--disable-infobars")
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-dev-shm-usage")

        # Tắt DevTools Protocol và các lỗi liên quan đến rendering
        edge_options.add_argument("--disable-features=VizDisplayCompositor")
        edge_options.add_argument("--remote-debugging-port=0")

        try:
            seleniumwire_options = {}
            if self.proxy:
                proxy = self.proxy
                seleniumwire_options['proxy'] = {
                    'http': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                    'https': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                    'no_proxy': 'localhost, 127.0.0.1'
                }
                
            service = EdgeService(EdgeChromiumDriverManager().install())
            # Cài đặt và khởi tạo WebDriver cho Edge
            driver = webdriver.Edge(service=service, options=edge_options,seleniumwire_options=seleniumwire_options)
            logging.info("Edge browser started successfully.")
            return driver
        except Exception as e:
            logging.error(f"Error starting Edge browser: {e}")
            raise e

    def cleanup(self):
        """Remove temporary directory if created."""
        if hasattr(self, 'profile_dir') and self.profile_dir:
            import shutil
            shutil.rmtree(self.profile_dir, ignore_errors=True)
