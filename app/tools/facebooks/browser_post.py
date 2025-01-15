from tools.driver import Browser
from time import sleep
from extensions.auth_proxy import create_proxy_extension,check_proxy
from sql.accounts import Account
from tools.facebooks.handle_browser_push import Push
from sql.errors import Error
import logging
from main.post import get_post_process_instance

account_instance = Account()
error_instance = Error()
post_process_instance = get_post_process_instance()

def process_post(account,stop_event):
    browser = None
    manager = None
    
    post_process_instance.update_process(account.get('id'),'Bắt đầu')
    logging.info(f'=========={account["name"]}============')
    print(f'=========={account["name"]}============')
    while not stop_event.is_set():
        checkProxy = True
        dirextension = None
        proxy = account.get('proxy')
        if proxy:
            checkProxy = check_proxy(proxy)
            if checkProxy:
                dirextension = create_proxy_extension(proxy)
                post_process_instance.update_process(account.get('id'),'Đã tạo proxy')
        else:
            post_process_instance.update_process(account.get('id'),'Không dùng proxy')

        try:
            if checkProxy == True:
                manager = Browser(f"/push/{account['id']}/home",dirextension,loadContent=True)
                browser = manager.start()
                post_process_instance.update_process(account.get('id'),'Đã khởi tạo trình duyệt')
                break
            else:
                post_process_instance.update_process(account.get('id'),'Proxy không dùng được')
                raise Exception("Proxy không hợp lệ")
        except Exception as e:
            error_instance.insertContent(e)
            post_process_instance.update_process(account.get('id'),'Không thể khởi tạo trình duyệt, đợi 30s...')
            logging.error(f"Không thể khởi tạo trình duyệt, thử lại sau 30s...")
            print(f"Không thể khởi tạo trình duyệt, thử lại sau 30s...")
            sleep(30)
            account = account_instance.find(account['id'])
    
    try:
        post_process_instance.update_process(account.get('id'),'Chuyển hướng tới fb')
        browser.get("https://facebook.com")
        crawl = Push(browser,account,dirextension,manager)
        crawl.handle(stop_event)
        sleep(5)
    except Exception as e:
        logging.error(f"Lỗi trong push: {e}")
        print(f"Lỗi trong push: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

