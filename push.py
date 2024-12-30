

import signal
import multiprocessing
import os
import shutil
from selenium.common.exceptions import WebDriverException
from base.browser import Browser
from facebook.push import Push
from time import sleep
import json
from helpers.inp import get_list_user_input
from sql.accounts import Account

account_instance = Account()

def process_push(user_id):
    browser = None
    manager = None
    account = account_instance.find(user_id)
    if 'id' not in account:
        print(f'Không tìm thấy user có id: {user_id}')
        return
    
    try:
        manager = Browser(user_id)
        browser = manager.start(False)
        browser.get("https://facebook.com")
        crawl = Push(browser,account)
        crawl.handle()
    except Exception as e:
        print(f"Lỗi trong Crawl: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

def push(ids):
    try:
        processes = []
        for id in ids:
            push_process = multiprocessing.Process(target=process_push,args=(id,))
            processes.extend([push_process])  
            push_process.start()
            sleep(2)

        for process in processes:
            process.join()

        print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
