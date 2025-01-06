
from selenium.webdriver.common.by import By
from sql.pages import Page
from base.browser import Browser
from sql.errors import Error
from facebook.type import types,push
from multiprocessing import Process
from sql.account_cookies import AccountCookies
from sql.accounts import Account
import json
from selenium.webdriver.common.action_chains import ActionChains
from helpers.modal import closeModal
from facebook.helpers import login,updateStatusAcount,updateStatusAcountCookie,handleCrawlNewFeed
from urllib.parse import urlparse, parse_qs
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
        while True:
            try:
                account = self.account_instance.find(self.account['id'])
                if account is None or 'id' not in account:
                    raise ValueError('Không tìm thấy tài khoản')
                self.account = account
                cookie = login(self.browser,self.account)
                updateStatusAcountCookie(cookie['id'], 2)
                print(f'==================Newsfeed ({account["name"]})================')
                updateStatusAcount(self.account['id'],3) # Đang lấy
                self.crawlNewFeed(account) # Bắt đầu quá trình crawl
                print('Đã duyệt xong, chờ 30s để tiếp tục...')
                sleep(30)
            except Exception as e:
                log_newsfeed(account,'Lỗi xảy ra, thử lại sau 5p....!')
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                updateStatusAcount(self.account['id'],1)
                if self.account.get('latest_cookie'): 
                    updateStatusAcountCookie(self.account['latest_cookie']['id'], 1)
                self.error_instance.insertContent(e)
                print("Thử lại sau 5 phút...")
                sleep(300)
            except KeyboardInterrupt: 
                if self.account.get('latest_cookie'): 
                    updateStatusAcountCookie(self.account['latest_cookie']['id'], 2)
                updateStatusAcount(self.account['id'],2)
                

    def crawlNewFeed(self,account):
        log_newsfeed(account,f"**********************************")
        checker = PageChecker(self.browser, self.dirextension)
        checker.run(account)
        

class PageChecker:
    def __init__(self, browser, dirextension):
        self.browser = browser
        self.dirextension = dirextension

    def run(self, account):
        # Xử lý page mới
        print(f"Chuyển hướng tới trang chủ!")
        # Mở trang cá nhân
        try:
            self.browser.get('https://facebook.com')
            sleep(2)
            profile_button = self.browser.find_element(By.XPATH, push['openProfile'])
            profile_button.click()
        except Exception as e:
            log_newsfeed(account,f"Không mở được modal trang cá nhân, đóng tài khoản (khả năng k login được)!")
            raise ValueError('Không thể mở trang cá nhân!')

        sleep(10)
        # Tìm tất cả các page
        allPages = self.browser.find_elements(By.XPATH, '//div[contains(@aria-label, "Switch to")]')
        print(f'Số fanpage để lướt: {len(allPages)}')

        for page in allPages:
            name = page.text.strip()
            print(f'=================={name}================')
            
            # Khởi tạo các process
            process = Process(target=handleCrawlNewFeed, args=(account, name, self.dirextension))
            process_get = Process(target=crawlNewFeed, args=(account, name,self.dirextension))
            process_get_two = Process(target=crawlNewFeed, args=(account, name,self.dirextension))
            try:
                # Bắt đầu các process
                process.start()
                process_get.start()
                process_get_two.start()

                # Đợi các process hoàn thành
                process.join()
                process_get.join()
                process_get_two.join()
            except Exception as e:
                print(f"Lỗi trong quá trình xử lý: {e}")
            finally:
                # Đảm bảo process được dừng nếu gặp lỗi
                if process.is_alive():
                    process.terminate()
                if process_get.is_alive():
                    process.terminate()
                if process_get_two.is_alive():
                    process.terminate()


    def terminate_processes(self, processes):
        """Hàm đóng tất cả tiến trình"""
        for process in processes:
            if process.is_alive():
                process.terminate()
                print(f"Đã dừng process: {process.pid}")