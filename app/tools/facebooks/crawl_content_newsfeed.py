
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
from time import sleep
from main.newsfeed import get_newsfeed_process_instance

newsfeed_process_instance = get_newsfeed_process_instance()

class CrawContentNewsfeed:
    def __init__(self, browser, account, dirextension,manager):
        self.browser = browser
        self.account = account
        self.dirextension = dirextension
        self.manager = manager
        self.page_instance = Page()
        self.error_instance = Error()
        self.account_cookies = AccountCookies()
        self.account_instance = Account()

    def handle(self,stop_event):
        loginInstance = HandleLogin(self.browser,self.account,newsfeed_process_instance)
        while not stop_event.is_set():
            try:
                newsfeed_process_instance.update_process(self.account.get('id'),'Bắt đầu xử lý')
                # log_newsfeed(self.account,f'* Bắt đầu ({self.account["name"]}) *')
                print(f'==================Newsfeed ({self.account["name"]})================')
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    raise ValueError('Không thể login')
                account = loginInstance.getAccount()
                newsfeed_process_instance.update_process(self.account.get('id'),'Đăng nhập thành công')
                self.account = account
                loginInstance.updateStatusAcount(self.account['id'],3) # Đang lấy
                self.crawlNewFeed(account,stop_event) 
                break
            except Exception as e:
                newsfeed_process_instance.update_process(self.account.get('id'),'Login thất bài, thử lại sau 5p...')
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                self.error_instance.insertContent(e)
                print("Thử lại sau 5 phút...")
                sleep(300)                

    def crawlNewFeed(self,account,stop_event):
        # log_newsfeed(account,f"**********************************")
        checker = PageChecker(self.browser, self.dirextension,self.manager)
        checker.run(account,stop_event)
        

def process_fanpage(account, name, dirextension, stop_event, managerDriver):
    print(f"Đang xử lý fanpage: {name}")
    threads = [
        Thread(target=handleCrawlNewFeed, args=(account, name, dirextension, stop_event, managerDriver)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event)),
    ]

    # Khởi chạy các thread
    for thread in threads:
        newsfeed_process_instance.update_task(account.get('id'),thread)
        thread.start()

    # Đợi tất cả các thread hoàn thành
    for thread in threads:
        thread.join()
    
    sleep(5)
    print(f"Hoàn thành xử lý fanpage: {name}")

class PageChecker:
    def __init__(self, browser, dirextension,manager):
        self.browser = browser
        self.manager = manager
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

            names = []
            if len(allPages) > 0: 
                for idx, page in enumerate(allPages):
                    if stop_event.is_set():
                        break

                    managerDriver = {
                        'manager': None,
                        'browser': None,
                    }
                    if idx == 0:
                        managerDriver = {
                            'manager': self.manager,
                            'browser': self.browser,
                        }

                    name = page.text.strip()
                    names.append(name)
                    names_str = ", ".join(names)  # Biến mảng thành chuỗi
                    newsfeed_process_instance.update_process(account.get('id'), f'Đang xử lý page: {names_str}')
                    print(f'=================={name}================')

                    # Khởi tạo các process
                    thread = Thread(target=process_fanpage, args=(account, name,self.dirextension, stop_event, managerDriver))
                    threads.append(thread)
                    thread.start()
                    sleep(2)
                    for thread in threads:
                        thread.join()
            else: 
                newsfeed_process_instance.update_process(account.get('id'), f'Không sở hữu fanpage nào!')


        except Exception as e:
            raise e