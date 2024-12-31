

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
from helpers.inp import get_list_user_input
from sql.accounts import Account

account_instance = Account()

def process_push(account,dirextension):
    browser = None
    manager = None
    
    try:
        manager = Browser(account['id'],dirextension)
        browser = manager.start(False)
        browser.get("https://facebook.com")
        newfeed = NewFeed(browser,account, dirextension)
        newfeed.handle()
        sleep(10)
    except Exception as e:
        print(f"Lỗi khi lấy bài new feed: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

def terminate_processes(processes):
    for process in processes:
        if process.is_alive():
            print(f"Đang dừng tiến trình PID: {process.pid}")
            process.terminate()
            process.join()

def newsfeed(ids,dirextension):
    try:
        print('\n==================== Lấy bài viết NewsFeed ====================')
        processes = []
        for id in ids:
            account = account_instance.find(id)
            if 'id' not in account:
                print(f'Không tìm thấy user có id: {id}')
                continue
            
            push_process = multiprocessing.Process(target=process_push,args=(account,dirextension))
            processes.extend([push_process])  
            push_process.start()
            crawl_nf = multiprocessing.Process(target=crawlNewFeed,args=(dirextension,))
            processes.extend([crawl_nf])  
            crawl_nf.start()
            sleep(2)

        for process in processes:
            process.join()
        print("Tất cả các tài khoản đã được xử lý.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
    finally:
        terminate_processes(processes)
