
from selenium.webdriver.common.by import By
from sql.pages import Page
from sql.errors import Error
from tools.types import push
from multiprocessing import Process
from sql.account_cookies import AccountCookies
from sql.accounts import Account
from threading import Thread, Event
from tools.facebooks.handle_craw_newsfeed import handleCrawlNewFeed,crawlNewFeed
from helpers.login import HandleLogin
# from helpers.logs import log_newsfeed
from time import sleep

class CrawContentNewsfeed:
    def __init__(self, browser, account, dirextension):
        self.browser = browser
        self.account = account
        self.dirextension = dirextension
        self.page_instance = Page()
        self.error_instance = Error()
        self.account_cookies = AccountCookies()
        self.account_instance = Account()

    def handle(self,stop_event):
        loginInstance = HandleLogin(self.browser,self.account)
        while not stop_event.is_set():
            try:
                # log_newsfeed(self.account,f'* Bắt đầu ({self.account["name"]}) *')
                print(f'==================Newsfeed ({self.account["name"]})================')
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    print('Đợi 5p rồi thử login lại!')
                    sleep(300)
                    continue
                account = loginInstance.getAccount()
                self.account = account
                loginInstance.updateStatusAcount(self.account['id'],3) # Đang lấy
                self.crawlNewFeed(account,stop_event) 
            except Exception as e:
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                self.error_instance.insertContent(e)
                print("Thử lại sau 5 phút...")
                sleep(300)                

    def crawlNewFeed(self,account,stop_event):
        # log_newsfeed(account,f"**********************************")
        checker = PageChecker(self.browser, self.dirextension)
        checker.run(account,stop_event)
        

def process_fanpage(account, name, dirextension, stop_event):
    print(f"Đang xử lý fanpage: {name}")

    threads = [
        Thread(target=handleCrawlNewFeed, args=(account, name, dirextension, stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event)),
    ]

    # Khởi chạy các thread
    for thread in threads:
        thread.start()

    # Đợi tất cả các thread hoàn thành
    for thread in threads:
        thread.join()

    print(f"Hoàn thành xử lý fanpage: {name}")

class PageChecker:
    def __init__(self, browser, dirextension):
        self.browser = browser
        self.error_instance = Error()
        self.dirextension = dirextension

    def run(self, account,stop_event):
        threads = []
        try:
            print(f"Đang ở trang chủ!")
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
                if stop_event.is_set():
                    break

                name = page.text.strip()
                print(f'=================={name}================')
                # Khởi tạo các process
                thread = Thread(target=process_fanpage, args=(account, name,self.dirextension, stop_event))
                threads.append(thread)
                thread.start()
                sleep(2)

            for thread in threads:
                thread.join()

        except Exception as e:
            raise e