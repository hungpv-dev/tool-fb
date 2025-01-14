import sys
from tools.driver import Browser
from tools.facebooks.browser_pages import BrowserFanpage
from time import sleep
from main.fanpage import get_fanpage_process_instance
from sql.system import System
from sql.errors import Error
from helpers.system import get_system_info
fanpage_process_instance = get_fanpage_process_instance()

def process_crawl(id, stop_event):
    system_instance = System()
    error_instance = Error()
    browser = None
    manager = None
    system = None
    fanpage_process_instance.update_process(id,'Đang mở tab....')
    while not stop_event.is_set(): 
        try:
            manager = Browser('/crawl',None,'chrome',True)
            browser = manager.start()
            fanpage_process_instance.update_process(id,'Đang chuyển hướng đến facebook....')
            browser.get("https://facebook.com")
            info = get_system_info()
            system = system_instance.insert({
                'info': info
            })
            crawl = BrowserFanpage(browser, system)
            crawl.handle(id,stop_event)
        except Exception as e:
            error_instance.insert(e)
            fanpage_process_instance.update_process(id,'Tab bị lỗi, thử lại sau 10s....')
            print(f"Lỗi trong Crawl, khởi động lại sau 10s: {e}")
            sleep(10)
        finally:
            fanpage_process_instance.update_process(id,'Lỗi xảy ra....')
            print(f'==> Đang đóng tab: {id}')
            if system:
                system_instance.update(system['id'], {'status': 2})
            if browser:
                browser.quit()
            sleep(10)

    fanpage_process_instance.update_process(id,'Tab đã bị đóng, xoá và chạy lại...')


