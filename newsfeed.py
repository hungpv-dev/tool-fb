

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
from facebook.helpers import updateStatusAcount
from helpers.inp import check_proxy
from sql.accounts import Account
from sql.errors import Error
from helpers.logs import log_newsfeed

account_instance = Account()
error_instance = Error()

def process_newsfeed(account):
    browser = None
    manager = None
    proxy = account.get('proxy')

    print(f'=========={account["name"]}============')
    while True:
        checkProxy = True
        proxy = account.get('proxy')
        updateStatusAcount(account['id'],2)
        if proxy:
            checkProxy = check_proxy(proxy)

        try:
            if checkProxy == True:
                manager = Browser(f"/newsfeed/{account['id']}/home",proxy)
                browser = manager.start()
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
        # browser.get('https://whatismyipaddress.com')
        # sleep(10000)
        browser.get("https://facebook.com")
        newfeed = NewFeed(browser,account,proxy)
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
        fullpath = os.path.abspath(f'./profiles/newsfeed')
        if os.path.exists(fullpath):
            shutil.rmtree(fullpath)  
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
