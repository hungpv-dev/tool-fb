

import signal
import multiprocessing
import os
import shutil
from selenium.common.exceptions import WebDriverException
from base.browser import Browser
from facebook.push import Push
from facebook.newfeed import NewFeed
from time import sleep
import json
from facebook.helpers import crawlNewFeed
from helpers.inp import terminate_processes
from extensions.auth_proxy import create_proxy_extension
from helpers.inp import check_proxy
from sql.accounts import Account

account_instance = Account()

def process_newsfeed(account):
    browser = None
    manager = None
    
    proxy = account.get('proxy')
    checkProxy = True
    dirextension = None
    if proxy:
        checkProxy = check_proxy(proxy)
        if checkProxy:
            dirextension = create_proxy_extension(proxy)

    if checkProxy == False:
        raise Exception(f"Không thể sử dụng proxy: {proxy['ip']}:{proxy['port']}")

    try:
        manager = Browser(f"/newsfeed/{account['id']}/home",dirextension)
        browser = manager.start()
        browser.get("https://facebook.com")
        newfeed = NewFeed(browser,account,dirextension)
        newfeed.handle()
        sleep(10)
    except Exception as e:
        print(f"Lỗi khi lấy bài new feed: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

def newsfeed(ids):
    try:
        print('\n==================== Lấy bài viết NewsFeed ====================')
        processes = []
        for id in ids:
            account = account_instance.find(id)
            if 'id' not in account:
                print(f'Không tìm thấy user có id: {id}')
                continue
            push_process = multiprocessing.Process(target=process_newsfeed,args=(account,))
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
