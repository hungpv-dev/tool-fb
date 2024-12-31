import json
from time import sleep
from selenium.webdriver.common.by import By
from sql.account_cookies import AccountCookies
from selenium.webdriver.common.action_chains import ActionChains
from facebook.type import types,push
from helpers.modal import closeModal
from sql.accounts import Account
from sql.pagePosts import PagePosts
from selenium.common.exceptions import StaleElementReferenceException
from sql.newsfeed import NewFeedModel
from base.browser import Browser
from sql.errors import Error
import unicodedata
from sql.account_cookies import AccountCookies
from urllib.parse import urlparse, parse_qs

def login(browser, account):
    try:
        if not account['latest_cookie']:
            raise ValueError("Không có cookie để đăng nhập.")

        last_cookie = account['latest_cookie']  
        cookies = last_cookie['cookies']
        for cookie in cookies:
            browser.add_cookie(cookie)
        
        sleep(1)
        browser.refresh()
        sleep(1)
        
        try:
            browser.find_element(By.XPATH, types['form-logout'])
        except Exception as e:
            updateStatusAcountCookie(last_cookie['id'],1)
            raise ValueError("Cookie không đăng nhập được.")
        print(f"Login {account['name']} thành công")
        return last_cookie
    except Exception as e:
        print(f"Lỗi khi login với cookie: {e}")
        raise  # Ném lỗi ra ngoài để catch trong hàm handle()
    
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
        
def handleCrawlNewFeed(account, name, dirextension = None):
    newfeed_instance = NewFeedModel()
    browserStart = Browser('hung',dirextension)
    browser = browserStart.start(False)
    browser.get("https://facebook.com")
    print(f'Chuyển hướng tới fanpage: {name}')
    cookie = login(browser,account)
    profile_button = browser.find_element(By.XPATH, push['openProfile'])
    profile_button.click()
    sleep(2)
    switchPage = browser.find_element(By.XPATH, push['switchPage'](name))
    switchPage.click()
    sleep(2)
    closeModal(1,browser)
    pageLinkPost = f"/posts/"
    pageLinkStory = "https://www.facebook.com/permalink.php"
    
    browser.execute_script("document.body.style.zoom='0.2';")
    sleep(3)
    
    listId = set() 
    while True: 
        listPosts = browser.find_elements(By.XPATH, types['list_posts']) 
        actions = ActionChains(browser)
        
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
                                post_id = ''
                                if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                                    if pageLinkPost in href:
                                        post_id = href.replace(pageLinkPost, '').split('?')[0]
                                        post_id = post_id.split('/')[-1]
                                    elif pageLinkStory in href:
                                        parsed_url = urlparse(href)
                                        query_params = parse_qs(parsed_url.query)
                                        post_id = query_params.get('story_fbid', [None])[0]
                                    if post_id == '': continue

                                    data = {
                                        'post_fb_id': post_id,
                                        'post_fb_link': href,
                                        'status': 1,
                                        'cookie_id': cookie['id'],
                                        'account_id': cookie['account_id'],
                                    }
                                    newfeed_instance.insert(data)
            except StaleElementReferenceException:
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

def crawlNewFeed(dirextension):
    from facebook.crawl import Crawl
    
    newfeed_instance = NewFeedModel()
    error_instance = Error()
    manager = Browser('hung',dirextension)
    browser = manager.start()
    browser.get('https://facebook.com')
    crawl_instance = Crawl(browser)
    
    while True:
        try:
            up = newfeed_instance.first()
            if up is None:
                print('Hiện chưa có bài viết nào cần lấy! chờ 1p để tiếp tục...')
                sleep(60)
                break
            id = up['id']
            browser.get(up['post_fb_link'])
            up['newfeed'] = 1
            up['id'] = up['post_fb_id']
            up['link'] = up['post_fb_link']
            data = crawl_instance.crawlContentPost({},up,{},True)
            
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
                crawl_instance.insertPostAndComment(post,comments,{},id)
            else:
                newfeed_instance.destroy(id)
            sleep(2)
        except Exception as e:
            newfeed_instance.destroy(id)
            error_instance.insertContent(e)


def push_list(posts,account):
    try:
        from base.browser import Browser
        from facebook.push import Push
        manager = Browser()
        browser = manager.start(False)
        # browser.get('https://facebook.com')
        # cookie = login(browser,account)
        # print(f"{account['name']} đăng {len(posts)}")
        sleep(5)
    except Exception as e:
        print(f'Lỗi khi xử lý đăng bài: {e}')
    finally: 
        if 'browser' in locals():
            pass
            # browser.quit()
