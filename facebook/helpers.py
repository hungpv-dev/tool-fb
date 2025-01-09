import json
from time import sleep
from selenium.webdriver.common.by import By
from sql.account_cookies import AccountCookies
from selenium.webdriver.common.action_chains import ActionChains
from facebook.type import types,push
from helpers.modal import closeModal
from facebook.login import HandleLogin
from sql.accounts import Account
from helpers.time import convert_to_db_format
import uuid
from sql.pagePosts import PagePosts
from selenium.common.exceptions import StaleElementReferenceException
from sql.newsfeed import NewFeedModel
from base.browser import Browser
from helpers.logs import log_newsfeed,log_push
from sql.system import System
from sql.errors import Error
import unicodedata
import os
from sql.account_cookies import AccountCookies
from urllib.parse import urlparse, parse_qs
from helpers.system import get_system_info

def login(browser, account):
    try:
        if not account['latest_cookie']:
            raise ValueError("Không có cookie để đăng nhập.")

        last_cookie = account['latest_cookie']  
        try:
            cookies = last_cookie['cookies']
            for cookie in cookies:
                browser.add_cookie(cookie)
        except Exception as e:
            raise ValueError("Không thể thêm cookie vào trình duyệt.")
        
        sleep(1)
        browser.get('https://facebook.com')
        updateStatusAcountCookie(last_cookie.get('id'),2)
        sleep(1)
    except Exception as e:
        if 'latest_cookie' in account and 'id' in account['latest_cookie']:
            updateStatusAcountCookie(account['latest_cookie']['id'], 1)
        print(f"Lỗi login {account.get('name')}: {e}")
    
def updateStatusAcountCookie(cookie_id, status):
        # 1: Chết cookie
        # 2: Cookie đang sống
        account_cookies = AccountCookies()
        account_cookies.update(cookie_id,{'status': status})
        
def updatePagePostInfo(id, data):
        # 1: Chưa thực thi,
        # 2: Đã thực thi,
        # 3: Đang thực thi,
        # 4: Đã xảy ra lỗi,
        # 5: Huỷ đăng
        page_post_instance = PagePosts()
        page_post_instance.update_status(id,data)
        
def updateStatusAcount(account_id, status):
        # 1: Lỗi cookie,
        # 2: Đang hoạt động,
        # 3: Đang lấy dữ liệu...,
        # 4: Đang đăng bài...
        account_instance = Account()
        account_instance.update_account(account_id, {'status_login': status})
        
def handleCrawlNewFeed(account, name, dirextension = None,stop_event=None):
    try:
        newfeed_instance = NewFeedModel()
        error_instance = Error()
        account_cookie_instance = AccountCookies()
        account_id = account.get('id', 'default_id')
        pathProfile = f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}"
        print(f'Chuyển hướng tới fanpage: {name}')

        manager = None
        browser = None

        while not stop_event.is_set():
            try:
                while not stop_event.is_set():
                    try:
                        manager = Browser(pathProfile,dirextension)
                        browser = manager.start()
                        sleep(5)
                        break
                    except Exception as e:
                        log_newsfeed(account,f"{name} k dùng được proxy, chờ 30s để thử lại")
                        sleep(30)
                loginInstance = HandleLogin(browser,account)
                

                while not stop_event.is_set():
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        print('Đợi 5p rồi thử login lại!')
                        sleep(300)
                    else:
                        account = loginInstance.getAccount()
                        break

                updateStatusAcount(account.get('id'),{'status_login': 3})

                sleep(2)
                try:
                    profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    profile_button.click()
                    sleep(10)
                except Exception as e:
                    print(f"Không thể mở profile: {name}")
                sleep(1)
                try:
                    switchPage = browser.find_element(By.XPATH, push['switchPage'](name))
                    switchPage.click()
                    sleep(10)
                except Exception as e:
                    print(f"Không thể chuyển hướng tới fanpage: {name}")
                
                sleep(2)
                closeModal(1,browser)
                pageLinkPost = f"/posts/"
                pageLinkStory = "https://www.facebook.com/permalink.php"
                
                browser.execute_script("document.body.style.zoom='0.2';")
                sleep(3)
                listId = set() 
                log_newsfeed(account,f"====================Thực thi cào fanpage {name}=====================")
                while not stop_event.is_set(): 
                    try:
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    except Exception as e:
                        raise e
                        
                    actions = ActionChains(browser)
                    
                    listPosts = browser.find_elements(By.XPATH, types['list_posts']) 
                    
                    for p in listPosts:
                        try:
                            idAreaPost = p.get_attribute('aria-posinset')
                            if idAreaPost not in listId:
                                listId.add(idAreaPost)
                                links = p.find_elements(By.XPATH, ".//a")
                                for link in links:
                                    if link.is_displayed() and link.size['width'] > 0 and link.size['height'] > 0:
                                        actions.move_to_element(link).perform()
                                        href = link.get_attribute('href')
                                        time = link.text.strip()
                                        converTime = convert_to_db_format(time)
                                        post_id = ''
                                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]) or converTime:
                                            if pageLinkPost in href:
                                                post_id = href.replace(pageLinkPost, '').split('?')[0]
                                                post_id = post_id.split('/')[-1]
                                            elif pageLinkStory in href:
                                                parsed_url = urlparse(href)
                                                query_params = parse_qs(parsed_url.query)
                                                post_id = query_params.get('story_fbid', [None])[0]
                                            if post_id == '': continue

                                            account_cookie_instance.updateCount(account['latest_cookie']['id'], 'counts')
                                            data = {
                                                'post_fb_id': post_id,
                                                'post_fb_link': href,
                                                'status': 1,
                                                'cookie_id': account['latest_cookie']['id'],
                                                'account_id': account.get('id'),
                                            }
                                            res = newfeed_instance.insert(data)
                                            # log_newsfeed(account, f"* +1 đường dẫn * {str(res.get('data', {}).get('id', 'Không có id'))}")

                        except Exception as e:
                            print("Phần tử đã không còn tồn tại, tìm lại phần tử.")
                            continue
                
                    if len(listId) >= 20:
                        browser.refresh() 
                        sleep(2)  
                        listId.clear() 
                        browser.execute_script("document.body.style.zoom='0.2';")
                        sleep(3)
                        print('Load lại trang!')
                    else:
                        browser.execute_script("window.scrollBy(0, 500);")
                    sleep(5)
            except Exception as e:
                error_instance.insertContent(e)
                log_newsfeed(account,'Lỗi khi xử lý lướt website, thử lại sau 30s')
                sleep(30)
            finally:
                if browser:  # Kiểm tra lại trước khi gọi quit()
                    browser.quit()
                if manager:
                    manager.cleanup()

    except Exception as e:
        error_instance.insertContent(e)
    finally:
        log_newsfeed(account,f"==========================Đóng fanpage {name}=================================")
        
def is_valid_link(href, post):
    """
    Kiểm tra xem URL có hợp lệ hay không:
    - Không chứa ID của bài viết.
    - Không phải là một tệp GIF.
    - Không phải là một URL của Facebook.
    """
    return post['id'] not in href and '.gif' not in href and 'https://www.facebook.com' not in href

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def crawlNewFeed(account,name,dirextension,stop_event=None):
    try:
        account_id = account.get('id', 'default_id')
        pathProfile = f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}"
        account_cookie_instance = AccountCookies()
        from facebook.crawl import Crawl
        system_instance = System()
        newfeed_instance = NewFeedModel()
        error_instance = Error()
        info = get_system_info()
        system = system_instance.insert({
            'info': info
        })
        print(f'Chuyển hướng tới fanpage: {name}')
        manager = None
        browser = None
        while not stop_event.is_set():
            try:
                while not stop_event.is_set():
                    try:
                        manager = Browser(pathProfile,dirextension)
                        browser = manager.start()
                        sleep(5)
                        break
                    except Exception as e:
                        log_newsfeed(account,f"Khi cào lưu db k dùng đc, chờ 30s để thử lại")
                        sleep(30)
                
                loginInstance = HandleLogin(browser,account)

                while not stop_event.is_set():
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        print('Đợi 5p rồi thử login lại!')
                        sleep(300)
                    else:
                        account = loginInstance.getAccount()
                        break

                updateStatusAcount(account.get('id'),{'status_login': 3})
                sleep(2)
                try:
                    profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    profile_button.click()
                    sleep(10)
                except Exception as e:
                    print(f"Không thể mở profile: {name}")
                sleep(1)
                try:
                    switchPage = browser.find_element(By.XPATH, push['switchPage'](name))
                    switchPage.click()
                    sleep(10)
                except Exception as e:
                    print(f"Không thể chuyển hướng tới fanpage: {name}")

                browser.get('https://facebook.com')
                sleep(2)
                crawl_instance = Crawl(browser)
                log_newsfeed(account,f"==> Lưu bài viết <==")
                while not stop_event.is_set():
                    try:
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    except Exception as e:
                        raise e

                    try:
                        up = newfeed_instance.first({'account_id': account['id']})
                        # log_newsfeed(account,'=> * sử lí lưu đb *')

                        if up is None:
                            print('Hiện chưa có bài viết nào cần lấy! chờ 1p để tiếp tục...')
                            sleep(60)
                            continue
                        id = up['id']
                        browser.get(up['post_fb_link'])
                        up['newfeed'] = 1
                        up['id'] = up['post_fb_id']
                        up['link'] = up['post_fb_link']
                        try:
                            data = crawl_instance.crawlContentPost({},up,{},True)
                        except Exception as e:
                            newfeed_instance.destroy(id)
                            continue

                        keywords = up.get('keywords') or []
                        check = False
                        
                        post = data.get('post')
                        comments = data.get('comments')
                        post['keywords'] = keywords
                        
                        post_content_no_accents = remove_accents(post['content'].lower())
                        if any(remove_accents(keyword.lower()) in post_content_no_accents for keyword in keywords):
                            check = True

                        for cm in comments:
                            comment_content_no_accents = remove_accents(cm['content'].lower())
                            if any(remove_accents(keyword.lower()) in comment_content_no_accents for keyword in keywords):
                                check = True

                        if keywords is None or len(keywords) == 0:
                            if 'media' in post and 'images' in post['media'] and 'videos' in post['media']:
                                if len(post['media']['images']) > 0 or len(post['media']['videos']) > 0:
                                    check = True


                        if check:
                            crawl_instance.likePost()
                            system_instance.update_count(system['id'])
                            account_cookie_instance.updateCount(account['latest_cookie']['id'], 'count_get')
                            crawl_instance.insertPostAndComment(post,comments,{},id)
                        else:
                            newfeed_instance.destroy(id)
                        sleep(2)
                    except Exception as e:
                        newfeed_instance.destroy(id)
            except Exception as e:
                error_instance.insertContent(e)
                log_newsfeed(account,'Lỗi khi cào lưu db, thử lại sau 30s')
                sleep(30)
            finally: 
                if system:
                    system_instance.update(system['id'], {'status': 2})
                if browser:
                    browser.quit()
                    manager.cleanup()
    except Exception as e:
        print(e)
        error_instance.insertContent(e)
    finally:
        log_newsfeed(account,f"========> Đóng cào lưu đb {name} <=============")


def push_list(posts,account,dirextension):
    from sql.pagePosts import PagePosts
    page_post_instance = PagePosts()
    error_instance = Error()
    from facebook.push import Push
    try:
        manager = Browser(f"/push/{account['id']}/{str(uuid.uuid4())}",dirextension,'chrome',False,True)
        browser = manager.start(False)
        loginInstance = HandleLogin(browser,account)
        sleep(3)
        browser.get('https://facebook.com')
        while True:
            checkLogin = loginInstance.loginFacebook()
            if checkLogin == False:
                print('Đợi 5p rồi thử login lại!')
                sleep(300)
            else:
                account = loginInstance.getAccount()
                break
        sleep(2)
        updateStatusAcount(account['id'],4)
        
        push = Push(browser,account,dirextension)
        print(f"{account.get('name')} => đăng: {len(posts)} bài viết")
        for post in posts:
            try:
                page = post.get('page')
                name = push.switchPage(page)
                push.push(page,post,name)
                page_post_instance.update_status(post['id'],{
                    'status':2,
                    'cookie_id': account['latest_cookie']['id']
                })
                sleep(2)
            except Exception as e:
                print(e)
                error_instance.insertContent(e)
                page_post_instance.update_status(post['id'],{
                    'status':4,
                    'cookie_id': account['latest_cookie']['id']
                })
        sleep(5)
    except Exception as e:
        print(f'Lỗi khi xử lý đăng bài: {e}')
    finally: 
        if 'browser' in locals():
            if browser:
                browser.quit()
                manager.cleanup()
        print('Kết thúc quá trình đăng bài.')

def push_page(page,account,dirextension):
    from sql.pagePosts import PagePosts
    from sql.errors import Error
    from facebook.push import Push
    from sql.account_cookies import AccountCookies
    error_instance = Error()
    page_post_instance = PagePosts()
    pathProfile = f"/push/{account['id']}/{str(uuid.uuid4())}"
    account_instance = AccountCookies()
    while True:
        try:
            manager = None
            browser = None
            while True:
                try:
                    manager = Browser(pathProfile,dirextension,'chrome',False,True)
                    browser = manager.start(False)
                    sleep(5)
                    break
                except Exception as e:
                    log_newsfeed(account,f"Khi cào lưu db k dùng đc, chờ 30s để thử lại")
                    sleep(30)
            loginInstance = HandleLogin(browser,account)
            while True:
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    print('Đợi 5p rồi thử login lại!')
                    sleep(300)
                else:
                    account = loginInstance.getAccount()
                    break
                
            sleep(2)
            push_instance = Push(browser,account,dirextension)
            sleep(3)
            while True:
                try:
                    browser.get('https://facebook.com')
                    sleep(3)
                    profile_button = browser.find_element(By.XPATH, push['openProfile'])
                except Exception as e:
                    raise e
                
                cookie = account.get('latest_cookie')
                pageUP = page_post_instance.get_page_up({'page_id': page["id"],'account_id':account['id']})
                if pageUP:
                    try:
                        updateStatusAcount(account['id'],4)
                        res = account_instance.updateCount(cookie.get('id'),'counts')
                        name = push_instance.switchPage(page)
                        push_instance.push(page,pageUP,name)
                        page_post_instance.update_status(pageUP['id'],{
                            'status':2,
                            'cookie_id': cookie['id']
                        })
                        awaitSleep = int(pageUP.get('await', 0)) * 60
                        print(f'=====>{name}: cần đợi {pageUP.get("await", 0)}p để đăng bài tiếp theo!')
                        sleep(awaitSleep)
                    except Exception as e:
                        error_instance.insertContent(e)
                        page_post_instance.update_status(pageUP['id'],{
                            'status':4,
                            'cookie_id': cookie['id']
                        })
                        sleep(5)
                else: 
                    print('Chưa có bài viết nào trong hàng chờ, chờ 1p để tiếp tục....')
                    sleep(60)
        except Exception as e:
            error_instance.insertContent(e)
            print(f'Lỗi khi theo dõi page: {e}')
        finally:
            if 'browser' in locals():
                if browser:
                    browser.quit()
                    manager.cleanup()
            log_push(account,f'** => Dừng theo dõi page: {page.get("name")}, chờ 5p để tiếp tục')
            sleep(300)