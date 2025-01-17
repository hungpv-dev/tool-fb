
from selenium.webdriver.common.by import By
from sql.pages import Page
from sql.errors import Error
from tools.types import push
from multiprocessing import Process
from sql.account_cookies import AccountCookies
from sql.accounts import Account
from threading import Thread, Event
from tools.facebooks.handle_craw_newsfeed import handleCrawlNewFeed,crawlNewFeed,handleCrawlNewFeedVie
from helpers.login import HandleLogin
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import uuid
from main.newsfeed import get_newsfeed_process_instance

newsfeed_process_instance = get_newsfeed_process_instance()

class CrawContentNewsfeed:
    def __init__(self, browser, account, dirextension, manager):
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
                newsfeed_process_instance.update_process(self.account.get('id'),'Bắt đầu đăng nhập')
                # log_newsfeed(self.account,f'* Bắt đầu ({self.account["name"]}) *')
                logging.info(f'==================Newsfeed ({self.account["name"]})================')
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
                newsfeed_process_instance.update_process(self.account.get('id'),'Login thất bài, thử lại sau 1p...')
                logging.error(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                print(f"Lỗi khi xử lý lấy dữ liệu!: {e}")
                self.error_instance.insertContent(e)
                logging.error("Thử lại sau 1 phút...")
                print("Thử lại sau 1 phút...")
                sleep(60)                

    def crawlNewFeed(self,account,stop_event):
        # log_newsfeed(account,f"**********************************")
        checker = PageChecker(self.browser, self.dirextension,self.manager)
        checker.run(account,stop_event)
        

def process_fanpage(account, name, dirextension, stop_event, managerDriver):
    logging.info(f"Đang xử lý fanpage: {name}")
    print(f"Đang xử lý fanpage: {name}")
    threads = [
        Thread(target=handleCrawlNewFeedVie, args=(account, managerDriver, stop_event)),
        Thread(target=handleCrawlNewFeed, args=(account, name, dirextension, stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event)),
        Thread(target=crawlNewFeed, args=(account, name, dirextension, stop_event)),
    ]

    # Khởi chạy các thread
    for thread in threads:
        newsfeed_process_instance.update_task(account.get('id'),thread)
        thread.start()
        sleep(3)

    # Đợi tất cả các thread hoàn thành
    for thread in threads:
        thread.join()
    
    account_instance = Account()
    try:
        acc = account_instance.find(account.get('id'))
        if acc.get('status_login') == 3:
            account_instance.update_account(account.get('id'),{'status_login': 2})
    except Exception as e:
        print(e)

    sleep(5)
    newsfeed_process_instance.update_process(account.get('id'), f'Chương trình đã bị dừng...')
    logging.info(f"Hoàn thành xử lý fanpage: {name}")
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
            logging.info(f"Đang ở trang chủ!")
            print(f"Đang ở trang chủ!")
            newsfeed_process_instance.update_process(account.get('id'),'Tìm số fanpage')
            try:
                # Chờ tối đa 10 giây để `profile_button` xuất hiện
                profile_button = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, push['openProfile']))
                )
                profile_button.click()

                # Chờ tối đa 10 giây để `allFanPage` xuất hiện
                try:
                    allFanPage = WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.XPATH, push['allProfile']))
                    )
                    allFanPage.click()
                except Exception as e:
                    pass
            except Exception as e:
                raise e

            sleep(10)
            # Tìm tất cả các page
            allPages = self.browser.find_elements(By.XPATH, '//div[contains(@aria-label, "Switch to")]')
            logging.info(f'Số fanpage để lướt: {len(allPages)}')
            print(f'Số fanpage để lướt: {len(allPages)}')
            newsfeed_process_instance.update_process(account.get('id'),f'Lấy được: {len(allPages)} page')

            names = []
            managerDriver = {
                'manager': self.manager,
                'browser': self.browser,
            }
            if len(allPages) > 0: 
                for idx, page in enumerate(allPages):
                    if stop_event.is_set():
                        break

                    name = page.text.strip()
                    names.append(name)
                    names_str = ", ".join(names)  # Biến mảng thành chuỗi
                    newsfeed_process_instance.update_process(account.get('id'), f'Xử lý page: {names_str}')
                    logging.info(f'=================={name}================')
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