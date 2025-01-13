
from selenium.webdriver.common.by import By
from sql.pages import Page
from sql.errors import Error
from sql.account_cookies import AccountCookies
from sql.accounts import Account
from selenium.webdriver.common.action_chains import ActionChains
from helpers.modal import closeModal
from urllib.parse import urlparse, parse_qs
from tools.types import types
from sql.history import HistoryCrawlPage
from time import sleep
from helpers.fb import clean_url_keep_params
from helpers.time import convert_to_db_format
from sql.system import System
from main.fanpage import get_fanpage_process_instance

fanpage_process_instance = get_fanpage_process_instance()

class BrowserFanpage:
    def __init__(self, browser,system = None):
        self.browser = browser
        self.system = system
        self.page_instance = Page()
        self.error_instance = Error()
        self.system_instance = System()
        self.account_cookies = AccountCookies()
        self.history_instance = HistoryCrawlPage()
        self.account_instance = Account()

    def handle(self,tab_id,stop_event):
        while not stop_event.is_set():
            try:
                self.crawl(tab_id,stop_event) 
            except Exception as e:
                self.error_instance.insertContent(e)
                print("Thử lại sau 3s...")
                sleep(3)
                raise e
          
    def crawl(self,tab_id,stop_event):
        while stop_event.is_set():
            his = None
            page = None
            try:
                page = self.page_instance.page_old()
                his = self.history_instance.insert({
                    'status': 1,
                    'page_id': page['id']
                })
                name = page.get('name')
                fanpage_process_instance.update_process(tab_id, f"Đang cào page: {name if name else 'Không thể truy cập'}...")
                link = page['link']
                self.browser.get(link)
                self.crawlIdFanpage(page,his)
            except Exception as e:
                if page:
                    self.page_instance.update_page(page['id'],{'status':1}) # Đang hoạt động
                if his:
                    self.history_instance.update(his['id'], {'status': 2})
                raise e
            finally:
                fanpage_process_instance.update_process(tab_id,'Đang chuyển hướng...')
                if page:
                    self.page_instance.update_page(page['id'],{'status':1}) # Đang hoạt động
                if his:
                    self.history_instance.update(his['id'], {'status': 2})

        
    def crawlIdFanpage(self, page, his):
        from tools.facebooks.crawl_content_post import CrawlContentPost
        crawl_instance = CrawlContentPost(self.browser)
        closeModal(0, self.browser)
        self.browser.execute_script("document.body.style.zoom='0.2';")
        sleep(1)
        closeModal(0,self.browser)
        sleep(5)
        try:
            name = self.updateInfoFanpage(page)
        except Exception as e:
            raise ValueError(f'Page {page["id"]} không thể truy cập!')
        print(f'====== {name} ======')
        
        pageLinkPost = f"{page['link']}/posts/"
        pageLinkStory = "https://www.facebook.com/permalink.php"
        listPosts = self.browser.find_elements(By.XPATH, types['list_posts'])
        print(f"Lấy được {len(listPosts)} bài viết")
        post_links = []
        try:
            actions = ActionChains(self.browser)
            for p in listPosts:
                links = p.find_elements(By.XPATH, ".//a")
                for link in links:
                    if link.size['width'] > 0 and link.size['height'] > 0:
                        actions.move_to_element(link).perform() # Hover vào danh sách thẻ a
                        href = link.get_attribute('href')
                        href = clean_url_keep_params(href)
                        time = link.text.strip()
                        if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                            post_links.append({
                                'href': href,
                                'time': time
                            })
        except:
            pass
        
        if(len(post_links) == 0):
            print('Không lấy được đường dẫn bài viết nào!')
            return
        
        post_data = []
        for linkData in post_links:
            link = linkData['href']
            time = linkData['time']
            converTime = convert_to_db_format(time)
            if pageLinkPost in link:
                post_id = link.replace(pageLinkPost, '').split('?')[0]
                post_exists = next((data for data in post_data if data['id'] == post_id), None)
                if post_exists is None:
                    post_data.append({'id': post_id, 'link': link})
                else:
                    if converTime:
                        post_exists['link'] = link

            elif pageLinkStory in link:
                parsed_url = urlparse(link)
                query_params = parse_qs(parsed_url.query)
                story_fbid = query_params.get('story_fbid', [None])[0]
                post_exists = next((data for data in post_data if data['id'] == story_fbid), None)
                if post_exists is None:
                    post_data.append({'id': story_fbid, 'link': link})
                else:
                    if converTime:
                        post_exists['link'] = link

                    
        self.history_instance.update(his['id'],{'counts': len(post_data)})
        if post_data:
            for post in post_data:
                if self.system is not None:
                    self.system_instance.update_count(self.system['id'])
                crawl_instance.get(page, post, his)
        
        sleep(3)

    def updateInfoFanpage(self, page):
        dataUpdatePage = {}
        while True: 
            try:
                name_page = self.browser.find_element(By.XPATH, '(//h1)[last()]')
                name = name_page.text.strip()
                dataUpdatePage['name'] = name

                if name == 'This site can’t be reached':
                    print('Không load được trang đợi 30s,....')
                    sleep(30)
                    self.browser.refresh() 
                
                try:
                    verified_elements = name_page.find_elements(By.XPATH, types['verify_account'])
                    # Kiểm tra tích xanh
                    if verified_elements:
                        dataUpdatePage['verified'] = 1
                    else:
                        dataUpdatePage['verified'] = 0
                except:
                    dataUpdatePage['verified'] = 0
                    pass
                
                try: # Lấy lượt like
                    likes = self.browser.find_element(By.CSS_SELECTOR, types['friends_likes'])
                    dataUpdatePage['like_counts'] = likes.text
                except:
                    pass
                
                try: # Lấy follows
                    follows = self.browser.find_element(By.CSS_SELECTOR, types['followers'])
                    dataUpdatePage['follow_counts'] = follows.text
                except:
                    pass
                
                try: # Lấy followning
                    following = self.browser.find_element(By.CSS_SELECTOR, types['following'])
                    dataUpdatePage['following_counts'] = following.text
                except:
                    pass

                dataUpdatePage['status'] = 1
                self.page_instance.update_page(page['id'],dataUpdatePage)
                return name
            except Exception as e:
                self.page_instance.update_page(page['id'], {'status': 3})  # Không thể truy cập
                raise e
        
   
    