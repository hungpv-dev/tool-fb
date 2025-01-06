

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

account_instance = Account()

def process_push(account):
    browser = None
    manager = None
    
    while True:
        checkProxy = True
        dirextension = None
        proxy = account.get('proxy')
        updateStatusAcount(account['id'],2)
        if proxy:
            checkProxy = check_proxy(proxy)
            if checkProxy:
                dirextension = create_proxy_extension(proxy)

        try:
            manager = Browser(f"/push/{account['id']}/home",dirextension)
            browser = manager.start()
            break
        except Exception as e:
            print(e) 
            print(f"Không thể khởi tạo trình duyệt với proxy: {proxy['ip']}:{proxy['port']}, thử lại sau 3 phút...")
            updateStatusAcount(account['id'],6)
            log_push(account,"Lỗi k dùng được cookiew")
            sleep(180)
            account = account_instance.find(account['id'])
    
    if checkProxy == False:
        raise Exception(f"Không thể sử dụng proxy: {proxy['ip']}:{proxy['port']}")

    try:
        browser.get("https://facebook.com")
        crawl = Push(browser,account,dirextension)
        crawl.handle()
    except Exception as e:
        print(f"Lỗi trong push: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

def push(ids):
    try:
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
