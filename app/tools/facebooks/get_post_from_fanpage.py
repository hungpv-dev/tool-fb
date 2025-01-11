import sys
from tools.driver import Browser
from tools.facebooks.browser_pages import BrowserFanpage
from time import sleep
from main.fanpage import get_fanpage_process_instance
from sql.system import System
from helpers.system import get_system_info
fanpage_process_instance = get_fanpage_process_instance()

def process_crawl(id, stop_event):
    system_instance = System()
    browser = None
    manager = None
    system = None
    print(f'Đang mở tab: {id}')
    while not stop_event.is_set(): 
        try:
            fanpage_process_instance.update_process(id,'Đang mở tab....')
            manager = Browser('/crawl',None,'chrome',True)
            browser = manager.start()
            while not stop_event.is_set():
                try:
                    browser.get("https://facebook.com")
                    break
                except Exception as e:
                    print(f'=========\nĐang khởi động lại tab {id}!, chờ 10s ... \n{e}\n====================')
                    sleep(10)
            
            info = get_system_info()
            system = system_instance.insert({
                'info': info
            })
            crawl = BrowserFanpage(browser, system)
            crawl.handle(id)
        except Exception as e:
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


