from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.webdriver.edge.service import Service as EdgeService
# from selenium.webdriver.edge.options import Options as EdgeOptions
# from webdriver_manager.microsoft import EdgeChromiumDriverManager
import shutil
import logging
from tkinter import messagebox
import os


class Browser:
    def __init__(self, account='/hung', proxy=None, browser_type='chrome',anonymous=False,loadContent = False):
        self.account = account
        self.anonymous = anonymous
        self.loadContent = loadContent
        self.proxy = proxy
        self.browser_type = browser_type  # Chọn loại trình duyệt
        base_profile_dir = "./temp/profiles" + account
        
        if os.path.exists(base_profile_dir):
            if base_profile_dir != './temp/profiles/crawl':
                shutil.rmtree(base_profile_dir)

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
        from helpers.base import config
        chrome_options = Options()
        
        if self.profile_dir != './temp/profiles/crawl':
            full_path = os.path.abspath(self.profile_dir)
            chrome_options.add_argument(f"--user-data-dir={full_path}")
        if self.anonymous:
            chrome_options.add_argument("--incognito")

        headlessConfig = config('headless')
        if not headlessConfig:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--enable-unsafe-swiftshader")
            chrome_options.add_argument("--disable-webgl")
            chrome_options.add_argument("--use-gl=swiftshader")
        
        if not self.loadContent:
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
            service = Service(config('driver_path'))
            # service = Service('./tools/chromedriver.exe')
            # service = Service('./tools/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.set_page_load_timeout(120)
            driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled":True})
            
            return driver
        except Exception as e:
            logging.error(f"Error starting Chrome browser: {e}")
            # messagebox.showerror('Lỗi','Vui lòng tải driver')
            print(f"Error starting Chrome browser: {e}")
            raise e

    def cleanup(self):
        """Remove temporary directory if created."""
        if hasattr(self, 'profile_dir') and self.profile_dir:
            import shutil
            shutil.rmtree(self.profile_dir, ignore_errors=True)

