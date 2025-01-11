from selenium import webdriver
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
    def __init__(self, account='/hung', proxy=None, browser_type='chrome',anonymous=False,loadContent = False):
        self.account = account
        self.anonymous = anonymous
        self.loadContent = loadContent
        self.proxy = proxy
        self.browser_type = browser_type  # Chọn loại trình duyệt
        base_profile_dir = "./temp/profiles" + account
        
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
        if self.anonymous:
            chrome_options.add_argument("--incognito")

        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-webgl")
            chrome_options.add_argument("--use-gl=swiftshader")
        
        if self.loadContent == False:
            prefs = {
                "profile.managed_default_content_settings.images": 2,  # Tắt tải ảnh
                "profile.managed_default_content_settings.plugins": 2,  # Tắt tải video
                "profile.managed_default_content_settings.video": 2,  # Tắt tải video
                "disk-cache-size": 4096,  # Giới hạn kích thước cache
                "browser.cache.disk.enable": False,  # Tắt cache
                "browser.cache.memory.enable": False,  # Tắt cache trong bộ nhớ
            }
            chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-application-cache')
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--lang=en")

        try:
            if self.proxy:
                chrome_options.add_extension(self.proxy)
                # proxy = self.proxy
                # seleniumwire_options['proxy'] = {
                #     'http': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                #     'https': f'http://{proxy["user"]}:{proxy["pass"]}@{proxy["ip"]}:{proxy["port"]}',
                #     'no_proxy': 'localhost, 127.0.0.1'
                # }
            service = Service('./tools/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)
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

        if self.profile_dir != './profiles/crawl':
            full_path = os.path.abspath(self.profile_dir)
            edge_options.add_argument(f"--user-data-dir={full_path}")
            pass
        if self.anonymous:
            edge_options.add_argument("--incognito")

        if headless:
            edge_options.add_argument("--headless=new")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--enable-unsafe-swiftshader")
            edge_options.add_argument("--disable-webgl")
            edge_options.add_argument("--use-gl=swiftshader")
        
        if self.loadContent == False:
            prefs = {
                "profile.managed_default_content_settings.images": 2,  # Tắt tải ảnh
                "profile.managed_default_content_settings.plugins": 2,  # Tắt tải video
                "profile.managed_default_content_settings.video": 2,  # Tắt tải video
                "disk-cache-size": 4096,  # Giới hạn kích thước cache
                "browser.cache.disk.enable": False,  # Tắt cache
                "browser.cache.memory.enable": False,  # Tắt cache trong bộ nhớ
            }
            edge_options.add_experimental_option("prefs", prefs)
        edge_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        edge_options.add_argument("--disable-notifications")
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--ignore-ssl-errors')
        edge_options.add_argument('--disable-application-cache')
        edge_options.add_argument("--disable-translate")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--disable-infobars")
        edge_options.add_argument("--start-maximized")
        edge_options.add_argument("--disable-dev-shm-usage")

        try:
            service = EdgeService(executable_path="./msedgedriver")
            # Cài đặt và khởi tạo WebDriver cho Edge
            driver = webdriver.Edge(service=service, options=edge_options)
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

