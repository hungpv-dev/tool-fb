import signal
import multiprocessing
import os
import shutil
from selenium.common.exceptions import WebDriverException
from base.browser import Browser
from facebook.crawlid import CrawlId
from time import sleep
from helpers.inp import terminate_processes
from sql.system import System
from helpers.system import get_system_info

def process_crawl(count):
    system_instance = System()
    browser = None
    manager = None
    system = None
    print(f'Đang mở tab: {count}')
    while True: 
        try:
            manager = Browser('/crawl')
            browser = manager.start()
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
            print(f"Lỗi trong Crawl: {e}")
        finally:
            print(f'==> Đang đóng tab: {count}')
            if system:
                system_instance.update(system['id'], {'status': 2})
            if browser:
                browser.quit()
            sleep(10)

def crawl(countGet):
    try:
        processes = []
        for count in range(countGet):
            crawl_process = multiprocessing.Process(target=process_crawl,args=(count,))
            processes.append(crawl_process)
            crawl_process.start()
            sleep(2)

        for process in processes:
            process.join()
        print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    finally:
        terminate_processes(processes)
