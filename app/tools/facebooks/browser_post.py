from tools.driver import Browser
from time import sleep
from extensions.auth_proxy import create_proxy_extension,check_proxy
from sql.accounts import Account
from tools.facebooks.handle_browser_push import Push
from sql.errors import Error
import logging
from main.post import get_post_process_instance
from sql.system import System
from bot import send

account_instance = Account()
error_instance = Error()
system_instance = System()
post_process_instance = get_post_process_instance()

def process_post(account,stop_event):
    browser = None
    manager = None
    system_account = system_instance.create_account({
        'account_id': account.get('id'),
        'type': 3,
    })
    
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
            else:
                post_process_instance.update_process(account.get('id'),'Proxy không dùng được')
                raise Exception("Proxy không hợp lệ")
        
            post_process_instance.update_process(account.get('id'),'Chuyển hướng tới fb')
            browser.get("https://facebook.com")
            crawl = Push(browser,account,dirextension,manager,system_account)
            crawl.handle(stop_event)
            sleep(5)
        except Exception as e:
            error_instance.insertContent(e)
            post_process_instance.update_process(account.get('id'),'Trình duyệt bị đóng, đợi 30s...')
            system_instance.push_message(system_account.get('id'),'Không khởi tạo được trình duyệt')
            account = account_instance.find(account['id'])
        finally:
            if browser:
                browser.quit()
                manager.cleanup()
            logging.error(f"Trình duyệt bị đóng, thử lại sau 30s...")
            print(f"Trình duyệt bị đóng, thử lại sau 30s...")
            sleep(30)

    send(f"Tài khoản {account.get('name')} đã bị dừng đăng bài!")
    system_instance.update_account(system_account.get('id'),{'status': 2})
            
    
   
    

