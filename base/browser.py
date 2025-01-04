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
    def __init__(self, account='/hung', dirextension=None, browser_type='chrome'):
        self.account = account
        self.dirextension = dirextension
        self.browser_type = browser_type  # Chọn loại trình duyệt
        base_profile_dir = "./profiles" + account

        if not os.path.exists(base_profile_dir):
            os.makedirs(base_profile_dir)

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
            chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")

        if self.dirextension:
            chrome_options.add_extension(self.dirextension)

        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")

        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            service = Service('chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logging.error(f"Error starting Chrome browser: {e}")
            raise e

    def start_firefox(self, headless):
        firefox_options = FirefoxOptions()

        if self.profile_dir and self.profile_dir != '/profiles/crawl':
            firefox_options.set_preference("browser.download.dir", self.profile_dir)

        if headless:
            firefox_options.add_argument("--headless")

        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("intl.accept_languages", "en-US, en")

        try:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            if self.dirextension:
                print(self.dirextension)
                # driver.install_addon(self.dirextension)
            logging.info("Firefox browser started successfully.")
            return driver
        except Exception as e:
            logging.error(f"Error starting Firefox browser: {e}")
            raise e

    def start_edge(self, headless):
        edge_options = EdgeOptions()

        # Thêm tùy chọn cho profile người dùng nếu cần
        if self.profile_dir != '/profiles/crawl':
            edge_options.add_argument(f"--user-data-dir={self.profile_dir}")

        # Thêm extension nếu có
        if self.dirextension:
            edge_options.add_extension(self.dirextension)

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
            service = EdgeService(EdgeChromiumDriverManager().install())
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
