from time import sleep
from sql.posts import Post
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from facebook.type import types,push
from sql.pagePosts import PagePosts
from sql.pages import Page
from helpers.modal import closeModal
from sql.errors import Error
import json
from helpers.image import copy_image_to_clipboard
import requests
from facebook.crawlid import CrawlId
from sql.comment import Comment
from sql.account_cookies import AccountCookies
from io import BytesIO
from sql.accounts import Account
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
from helpers.logs import log_push
import threading
from PIL import Image
from facebook.login import HandleLogin
from facebook.helpers import login,updateStatusAcount,updateStatusAcountCookie,updatePagePostInfo,push_list,push_page


class Push:
    def __init__(self,browser,account,dirextension):
        self.browser = browser
        self.account = account
        self.dirextension = dirextension
        self.crawlid_instance = CrawlId(browser)
        self.post_instance = Post()
        self.page_instance = Page()
        self.error_instance = Error()
        self.comment_instance = Comment()
        self.account_instance = Account()
        self.account_cookie_instance = AccountCookies()
        self.pagePosts_instance = PagePosts()
        
    def handle(self):
        loginInstance = HandleLogin(self.browser,self.account)
        while True:
            try:
                log_push(self.account,f'* Bắt đầu ({self.account["name"]}) *')
                print(f'==================Push ({self.account["name"]})================')
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    print('Đợi 5p rồi thử login lại!')
                    sleep(300)
                    continue
                account = loginInstance.getAccount()
                self.account = account
                self.handleData();          
            except Exception as e:
                print(f"Lỗi khi xử lý đăng bài viết!: {e}")
                self.error_instance.insertContent(e)
                print("Thử lại sau 5 phút...")
                sleep(300)

    def handleData(self):    
        loginInstance = HandleLogin(self.browser,self.account)
        print('Bắt đầu xử lý dữ liệu')
        listPages = set()
        while True:
            try:
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    print("Chưa đăng nhập, tiếp tục kiểm tra...")
                    sleep(300)
                    continue

                while True: 
                    try:
                        listTimes = self.browseTime()
                        if(len(listTimes) > 0):
                            log_push(self.account,'Bắt đầu đăng bài')
                            worker_thread = threading.Thread(target=push_list, args=(listTimes,self.account,self.dirextension))
                            worker_thread.daemon = True  
                            worker_thread.start()
                        else:
                            print(f"{self.account.get('name')} chưa có bài nào cần đăng trong khung giờ này!")
                        
                        awaitListPage = self.getAwaitListPage()
                        for pot in awaitListPage:
                            if pot and 'id' in pot:
                                page_id = pot.get('id')  
                                if page_id not in listPages:
                                    log_push(self.account,f'=======Theo dõi: {pot.get("name")}')
                                    print(f'=======Theo dõi: {pot.get("name")}')
                                    worker_thread = threading.Thread(target=push_page, args=(pot,self.account,self.dirextension))
                                    worker_thread.daemon = True  # Dừng thread khi chương trình chính dừng
                                    worker_thread.start()
                                    listPages.add(page_id)
                    except Exception as e:
                        print(e)
                    print('Chờ 60s để tiếp tục...')
                    sleep(60)
   
            except Exception as e:
                print(f'Lỗi khi push: {e}')
                print('Chờ 5 phút trước khi thử lại...')
                sleep(300)

            
    
    def browseTime(self):
        listPosts = self.pagePosts_instance.get_post_time({'account_id': self.account['id']})
        return listPosts
        

    def getAwaitListPage(self):
        listPosts = self.pagePosts_instance.get_post_list({'user_id': self.account['id']})
        return listPosts
        
    
    def getListPage(self):
        while True:
            try:
                listPages = self.page_instance.get_pages({
                    'type_page': 2,
                    'user_id': self.account["id"],
                    'order': 'updated_at',
                    'sort': 'asc',
                    'show_all': True,
                })['data']
                if listPages: 
                    print(f"Lấy được danh sách trang: {len(listPages)} trang.")
                    return listPages
                else:
                    print("Không có dữ liệu. Đợi 5 phút trước khi thử lại...")
            except Exception as e:
                print(f"Lỗi khi lấy danh sách trang: {e}")

            sleep(300)



    # Xử lý đăng
    def switchPage(self, page):
        name = page['name']
        try:
            self.browser.get(page['link'])
            sleep(2)
            name = self.crawlid_instance.updateInfoFanpage(page)
        except Exception as e:
            pass
        print('-> Mở popup thông tin cá nhân!')
        profile_button = self.browser.find_element(By.XPATH, push['openProfile'])
        sleep(5)
        profile_button.click()
        sleep(3)
        try:
            switchPage = self.browser.find_element(By.XPATH, push['switchPage'](name))
            switchPage.click()
        except Exception as e:
            print("-> Không tìm thấy nút chuyển hướng tới trang quản trị!")
        sleep(3)
        return name
        
    def push(self,page,post,name):
        self.browser.get(page['link'])
        # sleep(2)
        # self.browser.execute_script("document.body.style.zoom='0.4';")
        sleep(2)
        try:
            print('==> Bắt đầu đăng bài')
            # Check nút button
            createPost = None
            for create in push['createPost']:
                try:
                    createPost = self.browser.find_element(By.XPATH,f'//*[contains(text(), "{create}")]')
                    break
                except:
                    continue
                
            if not createPost:
                raise ValueError(f"Không tìm thấy nút createPost trên trang {page['name']}")
            
            try:
                createPost.click()
            except:
                raise ValueError(f"Không thể click nút tạo bài viết!")
            
            sleep(1)
            input_element = self.browser.switch_to.active_element
            print('- Gán nội dung bài viết!')
            input_element.send_keys(post['content'])
            media = post['media']
            if media is not None: 
                images = media['images']
                if images is not None and len(images) > 0:
                    print('- Copy và dán hình ảnh')
                    for src in images:
                        sleep(1)
                        # Copy hình ảnh vào clipboard
                        copy_image_to_clipboard(src)
                        sleep(2)
                        input_element.send_keys(Keys.CONTROL, 'v')
                        sleep(2)
            sleep(5)
            print('Đăng bài')
            parent_form = input_element.find_element(By.XPATH, "./ancestor::form")
            parent_form.submit()
            sleep(10)
            try:
                pass
                closeModal(1,self.browser,True)
            except:
                pass
            sleep(10)
            self.afterUp(page,post,name) # Lấy link bài viết vừa đăng
            sleep(2)
            print('\n--------- Đăng bài thành công ---------\n')
        except Exception as e:
            raise e
        except KeyboardInterrupt:
            raise ValueError('Chương trình bị dừng!')
    
    def afterUp(self,page, up,name):
        # self.browser.get(page['link'])
        # sleep(2)
        # self.browser.execute_script("document.body.style.zoom='0.4';")
        sleep(2)
        pageLinkPost = f"{page['link']}/posts/"
        pageLinkStory = "https://www.facebook.com/permalink.php"
        link_up = ''
        try:
            # Chờ modal xuất hiện
            modal = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@aria-posinset="1"]'))
            )
            actions = ActionChains(self.browser)
            # Chờ các liên kết bên trong modal
            links = WebDriverWait(self.browser, 10).until(
                lambda browser: modal.find_elements(By.XPATH, ".//a")
            )
            for link in links:
                # Kiểm tra nếu phần tử có kích thước hiển thị
                if link.size['width'] > 0 and link.size['height'] > 0:
                    try:
                        # Hover vào phần tử
                        actions.move_to_element(link).perform()
                        sleep(0.5)  # Đợi một chút để URL được cập nhật
                        # Lấy URL thật
                        href = link.get_attribute('href')
                        if href:  # Chỉ thêm nếu href không rỗng
                            if any(substring in href for substring in [pageLinkPost, pageLinkStory]):
                                link_up = href
                                break
                                
                    except Exception as hover_error:
                        print(f"Lỗi khi hover vào liên kết: {hover_error}")
        except Exception as e:
            self.error_instance.insertContent(e)
            print(f"Không tìm thấy bài viết vừa đăng! {e}")
        
        print('Đã lấy được link up')
        updatePagePostInfo(up['id'],{'link_up': link_up}) # Cập nhật trạng thái đã đăng
        sleep(2)
        
        comments = up.get('comments', [])
        if comments and len(comments) > 0:
            self.browser.get(link_up)  
            sleep(3)

            try:
                inpComment = self.browser.find_element(By.XPATH, push['comments'](name))
                
                for comment in comments:
                    inpComment.click()  # Focus vào ô input
                    inpComment.send_keys(comment['content'])  # Nhập nội dung comment
                    inpComment.send_keys(Keys.ENTER)
                    sleep(3)
                    self.comment_instance.update_pp(comment['id'],{'status': 2})
            except Exception as e:
                print(f"Lỗi khi xử lý comment: {e}")
                
                
        
        
    