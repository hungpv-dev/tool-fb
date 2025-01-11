import sys
from selenium.common.exceptions import WebDriverException
from base.browser import Browser
from facebook.crawlid import CrawlId
from time import sleep
from helpers.inp import terminate_processes
from sql.system import System
from helpers.system import get_system_info
import threading

def process_crawl(count):
    system_instance = System()
    browser = None
    manager = None
    system = None
    print(f'Đang mở tab: {count}')
    while True: 
        try:
            manager = Browser('/crawl',None,'chrome',True)
            browser = manager.start(False)
            while True:
                try:
                    browser.get("https://facebook.com")
                    info = get_system_info()
                    system = system_instance.insert({
                        'info': info
                    })
                    break
                except Exception as e:
                    print(f'=========\nĐang khởi động lại tab {count}!, chờ 10s ... \n{e}\n====================')
                    sleep(10)

            crawl = CrawlId(browser, system)
            crawl.handle()
        except Exception as e:
            print(f"Lỗi trong Crawl, khởi động lại sau 10s: {e}")
            sleep(10)
        finally:
            print(f'==> Đang đóng tab: {count}')
            if system:
                system_instance.update(system['id'], {'status': 2})
            if browser:
                browser.quit()
            sleep(10)

def crawl(countGet):
    try:
        threads = []
        for count in range(countGet):
            thread = threading.Thread(target=process_crawl, args=(count,))
            threads.append(thread)
            thread.start()
            sleep(1)


        for thread in threads:
            thread.join()

        print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    finally:
        print("Đang đóng tất cả tài nguyên...")
        for thread in threads:
            print(f"Đang dừng thread {thread}")
        sys.exit(0)

