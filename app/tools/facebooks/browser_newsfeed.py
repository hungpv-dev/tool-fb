
from tools.driver import Browser
from tools.facebooks.crawl_content_newsfeed import CrawContentNewsfeed
from time import sleep
from extensions.auth_proxy import create_proxy_extension,check_proxy
from sql.accounts import Account
from sql.errors import Error
from main.newsfeed import get_newsfeed_process_instance


account_instance = Account()
error_instance = Error()
newsfeed_process_instance = get_newsfeed_process_instance()


def process_newsfeed(account, stop_event):
    browser = None
    manager = None
    
    print(f'=========={account["name"]}============')
    newsfeed_process_instance.update_process(account.get('id'),'Bắt đầu')

    while not stop_event.is_set():
        checkProxy = True
        extension = None
        proxy = account.get('proxy')
        if proxy:
            checkProxy = check_proxy(proxy)
            if checkProxy :
                extension = create_proxy_extension(proxy)
                newsfeed_process_instance.update_process(account.get('id'),'Đã tạo proxy')
        else:
            newsfeed_process_instance.update_process(account.get('id'),'Không dùng proxy')

        try:
            if checkProxy == True:
                manager = Browser(f"/newsfeed/home/{account['id']}",extension)
                browser = manager.start(False)
                newsfeed_process_instance.update_process(account.get('id'),'Đã khởi tạo trình duyệt')
                break
            else:
                newsfeed_process_instance.update_process(account.get('id'),'Proxy không dùng được')
                raise Exception("Proxy không hợp lệ")
        except Exception as e:
            error_instance.insertContent(e)
            newsfeed_process_instance.update_process(account.get('id'),'Không thể khởi tạo trình duyệt, đợi 30s...')
            print(f"Không thể khởi tạo trình duyệt, thử lại sau 30s...")
            sleep(30)
            account = account_instance.find(account['id'])

    try:
        # browser.get('https://whatismyipaddress.com')
        # sleep(10000)
        newsfeed_process_instance.update_process(account.get('id'),'Chuyển hướng tới facebook')
        browser.get("https://facebook.com")
        newfeed = CrawContentNewsfeed(browser,account,extension,manager)
        newfeed.handle(stop_event)
        sleep(5)
    except Exception as e:
        print(f"Lỗi khi lấy bài new feed: {e}")
    finally:
        if browser:
            browser.quit()
            manager.cleanup()

