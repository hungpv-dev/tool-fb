
from selenium.webdriver.common.by import By
from sql.pages import Page
from base.browser import Browser
from sql.errors import Error
from facebook.type import types,push
from multiprocessing import Process
from sql.account_cookies import AccountCookies
from sql.accounts import Account
import json
from threading import Thread, Event
from selenium.webdriver.common.action_chains import ActionChains
from helpers.modal import closeModal
from facebook.helpers import login,updateStatusAcount,updateStatusAcountCookie,handleCrawlNewFeed
from urllib.parse import urlparse, parse_qs
from facebook.login import HandleLogin
from helpers.logs import log_newsfeed
from time import sleep
from facebook.helpers import crawlNewFeed

class NewFeed:
    def __init__(self, browser, account, dirextension):
        self.browser = browser
        self.account = account
        self.dirextension = dirextension
        self.page_instance = Page()
        self.error_instance = Error()
        self.account_cookies = AccountCookies()
        self.account_instance = Account()

    def handle(self):
        loginInstance = HandleLogin(self.browser,self.account)
        while True:
            try:
                log_newsfeed(self.account,f'* Bắt đầu ({self.account["name"]}) *')
                print(f'==================Newsfeed ({self.account["name"]})================')
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    print('Đợi 5p rồi thử login lại!')
                    sleep(300)
                    continue
                account = loginInstance.getAccount()
                self.account = account
                updateStatusAcount(self.account['id'],3) # Đang lấy
                self.crawlNewFeed(account) # Bắt đầu quá trình crawl
                print('Đã duyệt xong, chờ 30s để tiếp tục...')
                sleep(30)
            except Exception as e:
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                self.error_instance.insertContent(e)
                print("Thử lại sau 5 phút...")
                sleep(300)                

    def crawlNewFeed(self,account):
        log_newsfeed(account,f"**********************************")
        checker = PageChecker(self.browser, self.dirextension)
        checker.run(account)
        

def process_fanpage(account, name, dirextension):

    stop_event = Event()

    # Tạo các threads để chạy đồng thời
    threads = [
        Thread(target=handleCrawlNewFeed, args=(account, name, dirextension,stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension,stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension,stop_event))
    ]

    # Khởi chạy các threads
    for thread in threads:
        thread.start()

    # Đợi các threads hoàn thành
    for thread in threads:
        thread.join()

class PageChecker:
    def __init__(self, browser, dirextension):
        self.browser = browser
        self.error_instance = Error()
        self.dirextension = dirextension

    def run(self, account):
        processes = []
        processed_pages = set()
        loginInstance = HandleLogin(self.browser,account)
        while True:
            try:
                print(f"Chuyển hướng tới trang chủ!")
                while True:
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        print('Đợi 5p rồi thử login lại!')
                        sleep(300)
                    else:
                        break
                    account = loginInstance.getAccount()

                try:
                    profile_button = self.browser.find_element(By.XPATH, push['openProfile'])
                    profile_button.click()
                except Exception as e:
                    raise e

                sleep(10)
                # Tìm tất cả các page
                allPages = self.browser.find_elements(By.XPATH, '//div[contains(@aria-label, "Switch to")]')
                print(f'Số fanpage để lướt: {len(allPages)}')

                for page in allPages:
                    name = page.text.strip()
                    if name in processed_pages:
                        # Bỏ qua page đã xử lý
                        continue
                    print(f'=================={name}================')
                    processed_pages.add(name)
                    # Khởi tạo các process
                    process = Process(target=process_fanpage, args=(account, name, self.dirextension))
                    processes.append(process)
                    process.start()
                    sleep(2)

                processes = [p for p in processes if p.is_alive()]
                print("Chờ 5 phút trước khi kiểm tra các page mới...")
                sleep(300)  # Chờ 5 phút trước khi lặp lại
            except Exception as e:
                processed_pages.clear()
                self.stop_all_processes(processes)
                self.error_instance.insertContent(e)
                log_newsfeed(account,'Lỗi khi xử lý newfeed, thử lại sau 50s')
                sleep(30)

    def stop_all_processes(processes):
        """Dừng tất cả các tiến trình đang chạy."""
        for process in processes:
            if process.is_alive():
                print(f"Dừng process {process.pid}")
                process.terminate()
        processes.clear()  