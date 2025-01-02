
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
                print('==================last login================')
                updateStatusAcount(self.account['id'],3) # Đang lấy
                self.crawlNewFeed(account) # Bắt đầu quá trình crawl
                print('Đã duyệt xong, chờ 30s để tiếp tục...')
                sleep(30)
            except Exception as e:
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
                

    def crawlNewFeed(self,account):
        print(f"Chuyển hướng tới trang chủ!")
        # Mở trang cá nhân
        self.browser.get('https://facebook.com')
        sleep(2)
        try:
            profile_button = self.browser.find_element(By.XPATH, push['openProfile'])
            profile_button.click()
            
        except: 
            raise ValueError('Không thể mở trang cá nhân!')
        
        sleep(5)
        
        try:
            allPages = self.browser.find_elements(By.XPATH, '//div[contains(@aria-label, "Switch to")]')
            print(f'Số fanpage để lướt: {len(allPages)}')
            processes = []
            dirextension = self.dirextension
            for page in allPages:
                name = page.text.strip()
                process = Process(target=handleCrawlNewFeed, args=(account,name,dirextension))
                processes.append(process)
                process.start()
                
                crawl_process_1 = Process(target=crawlNewFeed,args=(dirextension,))
                crawl_process_2 = Process(target=crawlNewFeed,args=(dirextension,))
                processes.extend([crawl_process_1])  
                processes.extend([crawl_process_2])  
                crawl_process_1.start()
                crawl_process_2.start() 
            
            for process in processes:
                process.join()
            print("Tất cả fanpage đã được xử lý.")
            
        except Exception as e: 
            raise ValueError(e)
        
