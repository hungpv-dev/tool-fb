import signal
import multiprocessing
import os
import shutil
from selenium.common.exceptions import WebDriverException
from base.browser import Browser
from facebook.crawlid import CrawlId
from time import sleep
from helpers.inp import get_user_input
from sql.system import System
from helpers.system import get_system_info


def process_crawl():
    system_instance = System()
    browser = None
    manager = None
    system = None
    try:
        manager = Browser()
        browser = manager.start()
        browser.get("https://facebook.com")
        info = get_system_info()
        system = system_instance.insert({
            'info': info
        })
        crawl = CrawlId(browser,system)
        crawl.handle()
        
    except Exception as e:
        print(f"Lỗi trong Crawl: {e}")
    finally:
        if system:
            system_instance.update(system['id'],{'status':2})
        if browser:
            browser.quit()
            manager.cleanup()

def crawl(countGet):
    try:
        processes = []
        for count in range(countGet):
            crawl_process = multiprocessing.Process(target=process_crawl)
            processes.extend([crawl_process])  
            crawl_process.start()
            sleep(2)

        for process in processes:
            process.join()

        print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
