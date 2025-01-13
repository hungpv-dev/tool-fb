from time import sleep
from sql.posts import Post
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tools.types import push
from sql.pagePosts import PagePosts
from sql.pages import Page
from helpers.modal import closeModal
from sql.errors import Error
import uuid
from helpers.fb import clean_url_keep_params
from helpers.image import delete_image,download_image
from tools.facebooks.browser_pages import BrowserFanpage
from sql.comment import Comment
from sql.account_cookies import AccountCookies
from sql.accounts import Account
from selenium.webdriver.common.action_chains import ActionChains
import threading
from helpers.login import HandleLogin
from tools.facebooks.func_handle_push_post import push_page,push_list
from main.post import get_post_process_instance

post_process_instance = get_post_process_instance()

class Push:
    def __init__(self,browser,account,dirextension,manager):
        self.browser = browser
        self.account = account
        self.manager = manager
        self.dirextension = dirextension
        self.crawlid_instance = BrowserFanpage(browser)
        self.post_instance = Post()
        self.page_instance = Page()
        self.error_instance = Error()
        self.comment_instance = Comment()
        self.account_instance = Account()
        self.account_cookie_instance = AccountCookies()
        self.pagePosts_instance = PagePosts()
        
    def handle(self,stop_event):
        loginInstance = HandleLogin(self.browser,self.account,post_process_instance)
        while not stop_event.is_set():
            try:
                post_process_instance.update_process(self.account.get('id'),'Bắt đầu đăng nhập')
                print(f'==================Push ({self.account["name"]})================')
                checkLogin = loginInstance.loginFacebook()
                if checkLogin == False:
                    raise ValueError('Không thể login')
                account = loginInstance.getAccount()
                post_process_instance.update_process(self.account.get('id'),'Đăng nhập thành công')
                self.account = account
                self.handleData(stop_event);          
                break
            except Exception as e:
                post_process_instance.update_process(self.account.get('id'),'Login thất bài, thử lại sau 1p...')
                print(f"Lỗi khi xử lý đăng bài viết!: {e}")
                self.error_instance.insertContent(e)
                print("Thử lại sau 1 phút...")
                sleep(60)

    def handleData(self,stop_event):    
        try:
            print(f"Đang ở trang chủ!")
        
            sleep(10)
            threads = []
            awaitListPage = self.getAwaitListPage()
            post_process_instance.update_process(self.account.get('id'),f'Đang xử lý {len(awaitListPage)} fanpage')
            for idx,pot in enumerate(awaitListPage):
                managerDriver = {
                    'manager': None,
                    'browser': None,
                }
                # if idx == 0:
                #     managerDriver = {
                #         'manager': self.manager,
                #         'browser': self.browser,
                #     }
                worker_thread = threading.Thread(target=push_page, args=(pot,self.account,self.dirextension,stop_event,managerDriver))
                worker_thread.daemon = True  # Dừng thread khi chương trình chính dừng
                worker_thread.start()
                threads.append(worker_thread)
                post_process_instance.update_task(self.account.get('id'),worker_thread)

            while not stop_event.is_set(): 
                try:
                    listTimes = self.browseTime()
                    if(len(listTimes) > 0):
                        worker_thread = threading.Thread(target=push_list, args=(listTimes,self.account,self.dirextension))
                        worker_thread.daemon = True  
                        worker_thread.start()
                        threads.append(worker_thread)
                        post_process_instance.update_task(self.account.get('id'),worker_thread)
                    else:
                        print(f"{self.account.get('name')} chưa có bài nào cần đăng trong khung giờ này!")
                    
                except Exception as e:
                    print(e)
                print('Chờ 60s để tiếp tục...')
                sleep(60)

            
            for thread in threads:
                thread.join()
            post_process_instance.update_process(self.account.get('id'), f'Chương trình đã bị dừng...')

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
            parent_form = input_element.find_element(By.XPATH, "./ancestor::form")
            media = post['media']
            listLinkTemps = []
            if media is not None: 
                photo_video_element = parent_form.find_element(By.XPATH, './/div[@aria-label="Photo/video"]')
                photo_video_element.click()
                try:
                    images = media['images']
                    if images is not None and len(images) > 0:
                        print('- Copy và dán hình ảnh')
                        for src in images:
                            temp_image_path = download_image(src, temp_file=f"image_{uuid.uuid4()}.png")
                            listLinkTemps.append(temp_image_path)
                            sleep(1)
                            file_input = parent_form.find_elements(By.XPATH, './/input[@type="file"]')[-1]
                            file_input.send_keys(temp_image_path)
                            sleep(3)
                except Exception as e:
                    print(f'Lỗi khi thêm hình ảnh: {e}')
            sleep(5)
            print('Đăng bài')
            parent_form.submit()
            sleep(10)
            try:
                pass
                closeModal(1,self.browser,True)
            except:
                pass
            sleep(10)
            for file in listLinkTemps:
                # Bước 3: Xóa file tạm sau khi gửi
                delete_image(file)
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
                        href = clean_url_keep_params(href)
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
        page_post_instance = PagePosts()
        page_post_instance.update_status(up['id'],{'link_up': link_up})
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
                
                
        
        
    