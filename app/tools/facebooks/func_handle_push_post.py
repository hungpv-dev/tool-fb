import uuid
from tools.driver import Browser
from time import sleep
from helpers.login import HandleLogin
from tools.types import push as pushType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from sql.pagePosts import PagePosts
from sql.errors import Error
from sql.account_cookies import AccountCookies
import logging


from main.post import get_post_process_instance
post_process_instance = get_post_process_instance()

def push_page(page,account,dirextension,stop_event):
    from tools.facebooks.browser_post import Push
    error_instance = Error()
    name = page.get('name')
    page_post_instance = PagePosts()
    pathProfile = f"/push/{account['id']}/{str(uuid.uuid4())}"
    account_instance = AccountCookies()


    while not stop_event.is_set():
        manager = None
        browser = None
        try:
            if not isinstance(manager,Browser):
                while not stop_event.is_set():
                    try:
                        manager = Browser(pathProfile,dirextension,'chrome',False,loadContent=True)
                        browser = manager.start()
                        sleep(5)
                        break
                    except Exception as e:
                        logging.error('Không tạo được trình duyệt')
                        print('Không tạo được trình duyệt')
                        sleep(30)

                loginInstance = HandleLogin(browser,account)
                while not stop_event.is_set():
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        post_process_instance.update_process(account.get('id'),'Không login được, đợi 1p')
                        logging.error('Đợi 1p rồi thử login lại!')
                        print('Đợi 1p rồi thử login lại!')
                        sleep(60)
                    else:
                        account = loginInstance.getAccount()
                        break
                sleep(15)
                    
            sleep(2)
            push_instance = Push(browser,account,dirextension,manager)
            sleep(3)

            logging.error(f'Bắt đầu theo dõi page: {name}')
            print(f'Bắt đầu theo dõi page: {name}')
            while not stop_event.is_set():
                cookie = account.get('latest_cookie')
                pageUP = page_post_instance.get_page_up({'page_id': page["id"],'account_id':account['id']})
                if pageUP:
                    try:
                        post_process_instance.update_process(account.get('id'),f"Xử lý đăng bài: {pageUP['id']}")
                        res = account_instance.updateCount(cookie.get('id'),'counts')
                        name = push_instance.switchPage(page,stop_event)
                        profile_button = browser.find_element(By.XPATH, pushType['openProfile'])
                        push_instance.push(page,pageUP,name)
                        page_post_instance.update_status(pageUP['id'],{
                            'status':2,
                            'cookie_id': cookie['id']
                        })
                        awaitSleep = int(pageUP.get('await', 0)) * 60
                        logging.error(f'=====>{name}: cần đợi {pageUP.get("await", 0)}p để đăng bài tiếp theo!')
                        print(f'=====>{name}: cần đợi {pageUP.get("await", 0)}p để đăng bài tiếp theo!')
                        post_process_instance.update_process(account.get('id'),f"Đăng thành công bài {pageUP['id']}")
                        sleep(awaitSleep)
                    except NoSuchElementException as e:
                        page_post_instance.update_status(pageUP['id'], {'status': 1})
                        raise e
                    except Exception as e:
                        error_instance.insertContent(e)
                        page_post_instance.update_status(pageUP['id'],{
                            'status':4,
                            'cookie_id': cookie['id']
                        })
                        sleep(5)
                else: 
                    logging.error('Chưa có bài viết nào trong hàng chờ, chờ 1p để tiếp tục....')
                    print('Chưa có bài viết nào trong hàng chờ, chờ 1p để tiếp tục....')
                    sleep(60)
        except Exception as e:
            error_instance.insertContent(e)
            logging.error(f'Lỗi khi theo dõi page: {e}')
            print(f'Lỗi khi theo dõi page: {e}')
        finally:
            if 'browser' in locals():
                if browser:
                    browser.quit()
                    manager.cleanup()
            sleep(300)


def browseTime(account):
    pagePosts_instance = PagePosts()
    listPosts = pagePosts_instance.get_post_time({'account_id': account['id']})
    return listPosts

def push_list(account,dirextension,stop_event):
    page_post_instance = PagePosts()
    error_instance = Error()
    from tools.facebooks.browser_post import Push
    pathProfile = f"/push/{account['id']}/{str(uuid.uuid4())}"
    manager = None
    browser = None
    while not stop_event.is_set():
        try:
            manager = Browser(pathProfile,dirextension,'chrome',loadContent=True)
            browser = manager.start()
            loginInstance = HandleLogin(browser,account)
            sleep(3)
            browser.get('https://facebook.com')
            sleep(15)
            while not stop_event.is_set():
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    logging.error('Đợi 1p rồi thử login lại!')
                    print('Đợi 1p rồi thử login lại!')
                    sleep(60)
                else:
                    account = loginInstance.getAccount()
                    break
            sleep(2)
            push = Push(browser,account,dirextension,manager)
            while not stop_event.is_set():
                posts = browseTime(account)
                logging.error(f"{account.get('name')} => đăng: {len(posts)} bài viết")
                print(f"{account.get('name')} => đăng: {len(posts)} bài viết")
                if len(posts) > 0:
                    for post in posts:
                        try:
                            post_process_instance.update_process(account.get('id'),f"Xử lý đăng bài: {post['id']}")
                            page = post.get('page')
                            name = push.switchPage(page,stop_event)
                            profile_button = browser.find_element(By.XPATH, pushType['openProfile'])

                            push.push(page,post,name)
                            page_post_instance.update_status(post['id'],{
                                'status':2,
                                'cookie_id': account['latest_cookie']['id']
                            })
                            post_process_instance.update_process(account.get('id'),f"Đăng thành công bài: {post['id']}")
                            sleep(2)
                        except NoSuchElementException as e:
                            page_post_instance.update_status(post['id'], {'status': 1})
                            raise e
                        except Exception as e:
                            logging.error(e)
                            print(e)
                            error_instance.insertContent(e)
                            page_post_instance.update_status(post['id'],{
                                'status':4,
                                'cookie_id': account['latest_cookie']['id']
                            })
                else:
                    logging.error('Không có bài nào cần đăng trong thời gian này, đợi 30s...')
                    print('Không có bài nào cần đăng trong thời gian này, đợi 30s...')
                    sleep(30)
        except Exception as e:
            logging.error(f'Lỗi khi xử lý đăng bài: {e}')
            print(f'Lỗi khi xử lý đăng bài: {e}')
        finally: 
            if browser:
                browser.quit()
                manager.cleanup()
            logging.error('Lỗi khi đăng bài time,thử lại sau 30s')
            print('Lỗi khi đăng bài time,thử lại sau 30s')
            sleep(30)