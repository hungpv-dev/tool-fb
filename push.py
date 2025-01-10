

import signal
import multiprocessing
import os
import shutil
from selenium.common.exceptions import WebDriverException
from base.browser import Browser
from facebook.push import Push
from time import sleep
import json
from helpers.inp import terminate_processes
from sql.accounts import Account
from extensions.auth_proxy import create_proxy_extension
from facebook.helpers import updateStatusAcount
from helpers.inp import check_proxy
from helpers.logs import log_push
from sql.errors import Error

account_instance = Account()
error_instance = Error()

def process_push(account):
    browser = None
    manager = None
    
    while True:
        checkProxy = True
        dirextension = None
        proxy = account.get('proxy')

        print(f'=========={account["name"]}============')
        if proxy:
            checkProxy = check_proxy(proxy)
            if checkProxy:
                dirextension = create_proxy_extension(proxy)

        try:
            if checkProxy == True:
                manager = Browser(f"/push/{account['id']}/home",dirextension)
                browser = manager.start(False)
                break
            else:
                raise Exception("Proxy không hợp lệ")
        except Exception as e:
            error_instance.insertContent(e)
            print(f"Không thể khởi tạo trình duyệt, thử lại sau 30s...")
            updateStatusAcount(account['id'],6)
            sleep(30)
            account = account_instance.find(account['id'])
    
    try:
        browser.get("https://facebook.com")
        crawl = Push(browser,account,dirextension)
        crawl.handle()
        sleep(10)
    except Exception as e:
        print(f"Lỗi trong push: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

def push(ids):
    try:
        print('\n==================== Đăng bài viết ====================')
        fullpath = os.path.abspath(f'./profiles/push')
        if os.path.exists(fullpath):
            shutil.rmtree(fullpath)  
        processes = []
        for id in ids:
            account = account_instance.find(id)
            if 'id' not in account:
                print(f'Không tìm thấy user có id: {id}')
                continue
            push_process = multiprocessing.Process(target=process_push,args=(account,))
            processes.extend([push_process])  
            push_process.start()
            sleep(5)

        for process in processes:
            process.join()
        print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    finally:
        terminate_processes(processes)
