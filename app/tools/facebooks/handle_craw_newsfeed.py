from sql.newsfeed import NewFeedModel
from sql.errors import Error
from sql.account_cookies import AccountCookies
import uuid
from tools.driver import Browser
import json
import unicodedata
from time import sleep
from helpers.login import HandleLogin
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from helpers.fb import clean_url_keep_params
from tools.types import push,types
from helpers.modal import clickOk
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helpers.time import convert_to_db_format
from bot import send
import logging
from helpers.modal import closeModal,openProfile
from selenium.common.exceptions import NoSuchElementException

from main.newsfeed import get_newsfeed_process_instance

newsfeed_process_instance = get_newsfeed_process_instance()

from sql.system import System
system_instance = System()

def updateSystemMessage(system,message):
    if system:
        system_instance.push_message(system.get('id'),message)

def handleCrawlNewFeedVie(account, managerDriver,dirextension = None, stop_event=None,system_account=None):
    process = newsfeed_process_instance.show(account.get('id'))
    newfeed_instance = NewFeedModel()
    error_instance = Error()
    account_cookie_instance = AccountCookies()
    manager = managerDriver.get('manager')
    browser = managerDriver.get('browser')
    init = True
    while not stop_event.is_set():
        try:
            if not init:
                manager = Browser(f"/newsfeed/home/{account['id']}",dirextension)
                browser = manager.start()
            else:
                init = False
                
            while not stop_event.is_set():
                if process['status_vie'] == 1:
                    sleep(30)
                    process = newsfeed_process_instance.show(account.get('id'))
                    continue

                loginInstance = HandleLogin(browser,account)
                while not stop_event.is_set():
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        print('Đợi 1p rồi thử login lại!')
                        updateSystemMessage(system_account,'Login thất bại')
                        sleep(60)
                    else:
                        account = loginInstance.getAccount()
                        break
                sleep(2)
                closeModal(1,browser)
                pageLinkPost = f"/posts/"
                pageLinkStory = "https://www.facebook.com/permalink.php"
                
                browser.execute_script("document.body.style.zoom='0.2';")
                sleep(3)
                listId = set() 
                # log_newsfeed(account,f"====================Thực thi cào fanpage {name}=====================")
                while not stop_event.is_set() and process['status_vie'] == 2: 
                    updateSystemMessage(system_account,'Bắt đầu cào vie')
                    try:
                        clickOk(browser)
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    except NoSuchElementException as e:
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
                                        href = clean_url_keep_params(href)
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
                                                'post_fb_link': clean_url_keep_params(href),
                                                'status': 1,
                                                'cookie_id': account['latest_cookie']['id'],
                                                'account_id': account.get('id'),
                                            }
                                            res = newfeed_instance.insert(data)
                                            print(f"{account.get('name')}: {data.get('post_fb_link')}")
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
                    process = newsfeed_process_instance.show(account.get('id'))
                updateSystemMessage(system_account,'Tắt cào vie')
                sleep(30)
        except Exception as e:
            browser.quit()
            manager.cleanup()
            if browser:
                browser = None
            if manager:
                manager = None
            error_instance.insertContent(e)
            print(e)
            logging.error(e)
            print('Lỗi khi lướt vie')
            sleep(30)
            

def handleCrawlNewFeed(account, name, dirextension = None,stop_event=None,system_account=None):
    try:
        newfeed_instance = NewFeedModel()
        error_instance = Error()
        account_cookie_instance = AccountCookies()
        account_id = account.get('id', 'default_id')
        pathProfile = f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}"
        print(f'Chuyển hướng tới fanpage: {name}')

        manager = None
        browser = None
        sendNoti = True
        while not stop_event.is_set():
            try:
                while not stop_event.is_set():
                    try:
                        manager = Browser(pathProfile,dirextension)
                        browser = manager.start()
                        sleep(5)
                        break
                    except Exception as e:
                        # log_newsfeed(account,f"{name} k dùng được proxy, chờ 30s để thử lại")
                        sleep(30)
                
                loginInstance = HandleLogin(browser,account)

                while not stop_event.is_set():
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        updateSystemMessage(system_account,'Login thất bại')
                        print('Đợi 1p rồi thử login lại!')
                        sleep(60)
                    else:
                        account = loginInstance.getAccount()
                        break
                sleep(2)
                # try:
                #     profile_button = browser.find_element(By.XPATH, push['openProfile'])
                #     profile_button.click()
                #     sleep(10)
                # except Exception as e:
                #     print(f"Không thể mở profile: {name}")
                # sleep(1)

                loginInstance.updateStatusAcount(account.get('id'),3)
                
                try:
                    # try:
                    #     # Chờ tối đa 10 giây để `allFanPage` xuất hiện và click
                    #     allFanPage = WebDriverWait(browser, 10).until(
                    #         EC.presence_of_element_located((By.XPATH, push['allProfile']))
                    #     )
                    #     allFanPage.click()
                    # except Exception as e:
                    #     pass

                    # updateSystemMessage(system_account,f'Chuyển hướng sang page {name}')

                    # # Chờ tối đa 10 giây để `switchPage` xuất hiện và click
                    # switchPage = WebDriverWait(browser, 10).until(
                    #     EC.presence_of_element_located((By.XPATH, push['switchPage'](name)))
                    # )
                    # switchPage.click()
                    openProfile(browser,name)
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
                # log_newsfeed(account,f"====================Thực thi cào fanpage {name}=====================")
                while not stop_event.is_set(): 
                    try:
                        clickOk(browser)
                        profile_button = browser.find_element(By.XPATH, push['openProfile'])
                    except NoSuchElementException as e:
                        if sendNoti:
                            send(f"Tài khoản {account.get('name')} không thể đăng nhập!")
                            sendNoti = False
                        raise e
                        
                    sendNoti = True
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
                                        href = clean_url_keep_params(href)
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
                                                'post_fb_link': clean_url_keep_params(href),
                                                'status': 1,
                                                'cookie_id': account['latest_cookie']['id'],
                                                'account_id': account.get('id'),
                                            }
                                            res = newfeed_instance.insert(data)
                                            print(f"{name}: {data.get('post_fb_link')}")
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
                # log_newsfeed(account,'Lỗi khi xử lý lướt website, thử lại sau 30s')
                sleep(30)
            finally:
                if browser:  # Kiểm tra lại trước khi gọi quit()
                    browser.quit()
                    browser = None
                if manager:
                    manager.cleanup()
                    manager = None

    except Exception as e:
        error_instance.insertContent(e)
    finally:
        print(f"==========================Đóng fanpage {name}=================================")
        logging.info(f"==========================Đóng fanpage {name}=================================")

def crawlNewFeed(account,name,dirextension,stop_event=None,system_account=None):
    try:
        account_id = account.get('id', 'default_id')
        pathProfile = f"/newsfeed/{str(account_id)}/{str(uuid.uuid4())}"
        account_cookie_instance = AccountCookies()
        from tools.facebooks.crawl_content_post import CrawlContentPost
        newfeed_instance = NewFeedModel()
        error_instance = Error()
        print(f'Chuyển hướng tới fanpage: {name}')
        manager = None
        browser = None
        while not stop_event.is_set():
            try:
                while not stop_event.is_set():
                    try:
                        manager = Browser(pathProfile,dirextension)
                        browser = manager.start(False)
                        sleep(5)
                        break
                    except Exception as e:
                        # log_newsfeed(account,f"Khi cào lưu db k dùng đc, chờ 30s để thử lại")
                        sleep(30)
                
                loginInstance = HandleLogin(browser,account)

                while not stop_event.is_set():
                    checkLogin = loginInstance.loginFacebook()
                    if checkLogin == False:
                        updateSystemMessage(system_account,'Login thất bại')
                        print('Đợi 1p rồi thử login lại!')
                        sleep(60)
                    else:
                        account = loginInstance.getAccount()
                        break

                loginInstance.updateStatusAcount(account.get('id'),3)
                sleep(2)
                # try:
                #     profile_button = browser.find_element(By.XPATH, push['openProfile'])
                #     profile_button.click()
                #     sleep(10)
                # except Exception as e:
                #     print(f"Không thể mở profile: {name}")
                # sleep(1)
                try:
                    # try:
                    #     # Chờ tối đa 10 giây để `allFanPage` xuất hiện và click
                    #     allFanPage = WebDriverWait(browser, 10).until(
                    #         EC.presence_of_element_located((By.XPATH, push['allProfile']))
                    #     )
                    #     allFanPage.click()
                    # except Exception as e:
                    #     pass

                    # updateSystemMessage(system_account,f'Chuyển hướng page: {name}')
                    # # Chờ tối đa 10 giây để `switchPage` xuất hiện và click
                    # switchPage = WebDriverWait(browser, 10).until(
                    #     EC.presence_of_element_located((By.XPATH, push['switchPage'](name)))
                    # )
                    # switchPage.click()
                    openProfile(browser,name)
                    sleep(10)
                except Exception as e:
                    print(f"Không thể chuyển hướng tới fanpage: {name}")

                browser.get('https://facebook.com')
                sleep(2)
                crawl_instance = CrawlContentPost(browser)
                # log_newsfeed(account,f"==> Lưu bài viết <==")
                while not stop_event.is_set():
                    try:
                        clickOk(browser)
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
                        browser.get(clean_url_keep_params(up['post_fb_link']))
                        up['newfeed'] = 1
                        up['id'] = up['post_fb_id']
                        up['link'] = up['post_fb_link']
                        try:
                            data = crawl_instance.crawlContentPost({},up,{},newfeed=True)
                        except Exception as e:
                            newfeed_instance.destroy(id)
                            continue

                        check = False
                        
                        post = data.get('post')
                        comments = data.get('comments')
                        try:
                            keywords = up.get('keywords') or []
                            post['keywords'] = keywords
                            
                            post_content_no_accents = remove_accents(post['content'].lower())
                            if any(remove_accents(keyword.lower()) in post_content_no_accents for keyword in keywords):
                                check = True

                            for cm in comments:
                                comment_content_no_accents = remove_accents(cm['content'].lower())
                                if any(remove_accents(keyword.lower()) in comment_content_no_accents for keyword in keywords):
                                    check = True

                            # if keywords is None or len(keywords) == 0:
                            #     if 'media' in post and 'images' in post['media'] and 'videos' in post['media']:
                            #         if len(post['media']['images']) > 0 or len(post['media']['videos']) > 0:
                            #             check = True
                        except Exception as e:
                            print('Lỗi khi check keywords')

                        # print(post.get('content'))
                        if check:
                            print('Đã lấy được 1 bài lưu db')
                            crawl_instance.shareCopyLink()
                            crawl_instance.sharePostAndOpenNotify()
                            # icon = crawl_instance.likePost()
                            # post['icon'] = icon
                            closeModal(crawl_instance.index,browser)
                            sleep(1)
                            print(json.dumps({
                                'link': post.get('link_facebook'),
                                'icon': post.get('icon'),
                            },indent=4))
                            crawl_instance.viewImages(post)
                            crawl_instance.insertPostAndComment(post,comments,{},id)
                            account_cookie_instance.updateCount(account['latest_cookie']['id'], 'count_get')
                            browser.get('https://facebook.com')
                            sleep(2)
                        else:
                            print('Bài này k thỏa mã yêu cầu!')
                            newfeed_instance.destroy(id)
                        sleep(2)
                    except Exception as e:
                        newfeed_instance.destroy(id)
            except Exception as e:
                error_instance.insertContent(e)
                # log_newsfeed(account,'Lỗi khi cào lưu db, thử lại sau 30s')
                sleep(30)
            finally: 
                if browser:
                    browser.quit()
                    browser = None
                    manager.cleanup()
                    manager = None
    except Exception as e:
        print(e)
        error_instance.insertContent(e)
    finally:
        print(f"========> Đóng cào lưu đb {name} <=============")
        logging.info(f"========> Đóng cào lưu đb {name} <=============")


     
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])