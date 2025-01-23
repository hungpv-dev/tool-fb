import sys
from tools.driver import Browser
from tools.facebooks.browser_pages import BrowserFanpage
from time import sleep
from main.fanpage import get_fanpage_process_instance
from sql.errors import Error
import logging
from bot import send

fanpage_process_instance = get_fanpage_process_instance()

def process_crawl(id, stop_event):
    error_instance = Error()
    browser = None
    manager = None
    fanpage_process_instance.update_process(id,'Đang mở tab....')
    while not stop_event.is_set(): 
        try:
            manager = Browser('/crawl',None,'chrome',True)
            browser = manager.start()
            fanpage_process_instance.update_process(id,'Đang chuyển hướng đến facebook....')
            browser.get("https://facebook.com")
            crawl = BrowserFanpage(browser)
            crawl.handle(id,stop_event)
        except Exception as e:
            logging.error(f"Lỗi trong Crawl, khởi động lại sau 10s: {e}")
            print(f"Lỗi trong Crawl, khởi động lại sau 10s: {e}")
            fanpage_process_instance.update_process(id,'Tab bị lỗi, thử lại sau 10s....')
        finally:
            logging.error(f'==> Đang đóng tab: {id}')
            print(f'==> Đang đóng tab: {id}')
            if browser:
                browser.quit()
            sleep(10)

    send(f'Tab cào fanpage mã: {id} đã bị đóng')
    fanpage_process_instance.update_process(id,'Tab đã bị đóng, xoá và chạy lại...')


