
from facebook.type import types,removeString,removeDyamic,selectDyamic,removeComment
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from time import sleep
import re
from helpers.time import convert_to_db_format
import json
from helpers.modal import closeModal
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sql.posts import Post
from helpers.modal import closeModal
from sql.pages import Page
from sql.errors import Error
from sql.history import HistoryCrawlPage
from sql.accounts import Account
from sql.account_cookies import AccountCookies
from urllib.parse import urlparse, parse_qs
from sql.comment import Comment 

class Crawl:
    def __init__(self, browser):
        self.browser = browser
        self.page_instance = Page()
        self.history_instance = HistoryCrawlPage()
        self.post_instance = Post()
        self.comment_instance = Comment()
        self.error_instance = Error()
        self.account_instance = Account()
        self.account_cookies = AccountCookies()

    def get(self,page, post, his):
        try:
            self.browser.get(post['link'])
            sleep(1)
            closeModal(0,self.browser)
            sleep(1)
            self.crawlContentPost(page, post, his)
        except Exception as e:
            self.history_instance.update_count(his['id'], {'type': 'errors'})
            self.error_instance.insertContent(e)
            print(f'Lỗi khi cào: {e}')
            raise e
  
    def crawlContentPost(self,page, post, his, newfeed = False):
        from facebook.helpers import is_valid_link
        data = {
            'account_id': post.get('account_id') or 0,
            'cookie_id': post.get('cookie_id') or 0,
            'post_id': post["id"],
            'page_id': page.get('id') or 0,
            'history_id': his.get('id') or 0,
            'newfeed': post.get('newfeed') or 0,
            'link_facebook': post['link'],
            'media' : {
                'images': [],
                'videos': []
            },
            'up': 0,
        }
        dataComment = []
        closeModal(0, self.browser)
        sleep(2)
        print(f"Bắt đầu lấy dữ liệu bài viết")
        modal = None # Xử lý lấy ô bài viết
        for modalXPath in types['modal']:
            try:
                # Chờ cho modal xuất hiện
                modal = self.browser.find_element(By.XPATH, modalXPath)
                break
            except Exception as e:
                continue
        if not modal:
            raise ValueError('Không lấy được bài viết!')
        else:
            aria_posinset = modal.get_attribute("aria-posinset")
            if aria_posinset is not None:
                # closeModal(0, self.browser)
            # else:
                pass
                # closeModal(2, self.browser)
        

        # Lấy thời gian đăng
        timeUp = None
        linkTimeUp = modal.find_elements(By.TAG_NAME, "a")
        if linkTimeUp and len(linkTimeUp) > 0:
            for link in linkTimeUp:
                href_text = link.text.strip()
                cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', href_text)
                formatted_time = convert_to_db_format(cleaned_text)
                if formatted_time:
                    timeUp = formatted_time
                    break

        print('==> Thời gian đăng: ', timeUp)
        data['time_up'] = timeUp

        try:
            content = modal.find_element(By.XPATH, types['content'])
            contentText = content.text
            for string in removeString:
                contentText = contentText.replace(string, '')
            data['content'] = contentText.strip()
        except:
            print(f'Bài viết k có content')
            data['content'] = ''

        # Lấy ảnh và video
        media = None
        try:
            media = modal.find_element(By.XPATH,types['media'])
        except Exception:
            media = modal
            
        media = modal
        try:
            images = media.find_elements(By.XPATH, './/img')
            for img in images:
                src = img.get_attribute('src')
                if src and src.startswith('http') and "emoji.php" not in src:
                    data['media']['images'].append(img.get_attribute('src'))
                
            videos = media.find_elements(By.XPATH, './/video')
            for video in videos:
                data['media']['videos'].append(video.get_attribute('src'))
        except Exception as e:
            print(e)
            print(f'Bài viết k có ảnh hoặc video')
        try:
            like_share_element = modal.find_element(By.XPATH, types['dyamic'])
            listCount = like_share_element.text
            for string in removeDyamic:
                listCount = listCount.replace(string, '')

            listCount = listCount.split('\n')
            
            if listCount:
                data['like'] = listCount[1] if len(listCount) > 1 else 0
                for dyamic in listCount:
                    if selectDyamic['comment'] in dyamic:
                        data['comment'] = dyamic
                    if selectDyamic['share'] in dyamic:
                        data['share'] = dyamic
        except Exception as e:
            print(f"Không lấy được like, comment, share: {e}")
        # Lấy comment
        try:
            scroll = modal.find_element(By.XPATH,types['scroll'])
            self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll)
        except: 
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        
        try:
            comments = modal.find_elements(By.XPATH, types['comments'])
            print(f"Lấy được: {len(comments)} bình luận!")
            
            # Click vào các từ xem thêm
            for cm in comments:
                # Xóa ảnh trùng trong danh sách data['media']['images']
                try:
                    imgs_in_comment = cm.find_elements(By.CSS_SELECTOR, 'img')
                    for img in imgs_in_comment:
                        src = img.get_attribute('src')
                        if src in data['media']['images']:
                            data['media']['images'].remove(src)
                except:
                    pass
                # Xóa video trùng trong danh sách data['media']['videos']
                try:
                    videos_in_comment = cm.find_elements(By.CSS_SELECTOR, 'video')
                    for video in videos_in_comment:
                        src = video.get_attribute('src')
                        if src in data['media']['videos']:
                            data['media']['videos'].remove(src)
                except:
                    pass

                try:
                    xem_them = cm.find_element(By.XPATH, types['hasMore'])
                    if xem_them:
                        self.browser.execute_script("arguments[0].click();", xem_them)
                except:
                    pass
            countComment = 0
            for cm in comments:
                if countComment >= 10:
                    break
                textComment = ''
                link_comment = []
                try:
                    div_elements = cm.find_elements(By.XPATH, './div')[1]
                    div_2 = div_elements.find_elements(By.XPATH, './div')
                    
                    
                    if not div_2 or not div_2[0]: 
                        continue
                    textComment = div_2[0].text
                    
                    try:
                        if len(div_2) > 1:
                            a_tags = div_2[1].find_elements(By.XPATH, './/a') 
                            if not a_tags:
                                a_tags = div_2[0].find_elements(By.XPATH, './/a')  
                        elif len(div_2) > 0:
                            a_tags = div_2[0].find_elements(By.XPATH, './/a')
                        else:
                            a_tags = []
                        for a in a_tags:
                            try:
                                img_element = None
                                try:
                                    img_element = a.find_element(By.XPATH, 'preceding-sibling::img') 
                                except:
                                    pass
                                
                                if img_element:
                                    print("Thẻ <a> có thẻ <img> phía trước, không lấy href.")
                                else:
                                    href = a.get_attribute('href')
                                    if href and is_valid_link(href, post) and href not in link_comment:
                                        link_comment.append(href)
                            except Exception as e:
                                print(f"Lỗi khi lấy href: {e}")
                    except IndexError as ie:
                        print(f"Lỗi chỉ mục: {ie}")
                    except Exception as e:
                        print(f"Lỗi không xác định: {e}")
                        
                except:
                    countComment += 1
                    pass
                    
                for text in removeComment:
                    textComment = textComment.replace(text,'')

                textComment = textComment.strip()
                textArray = textComment.split('\n')

                if 'Top fan' in textComment:
                    user_name = textArray[1]
                    textContentComment = ' '.join(textArray[2:])
                else:
                    user_name = textArray[0]
                    textContentComment = ' '.join(textArray[1:])

                textContentComment = textContentComment.replace('Follow','').strip()
                
                if user_name == '' or textContentComment == '':
                    continue

                countComment += 1
                dataComment.append({
                    'user_name': user_name,
                    'content': textContentComment,
                    'link_comment': link_comment,
                })
            print(f"=> Lưu được {len(dataComment)} bình luận!")
        except Exception as e:
            print(e)
            print("Không lấy được bình luận!")


        if newfeed:
            return {
                'post': data,
                'comments': dataComment
            }
        self.insertPostAndComment(data,dataComment, his)
        
    def insertPostAndComment(self, data, dataComment, his, newfeedid = 0):
        # print(json.dumps(data, indent=4))
        # print(json.dumps(dataComment, indent=4))
        # sleep(10000)
        
        from sql.newsfeed import NewFeedModel
        newfeed_instance = NewFeedModel()
        print("Đang lưu bài viết và bình luận vào database...")
        try:
            res = self.post_instance.insert_post({
                'post' : data,
                'comments': dataComment
            })

            print('==> Thời gian đăng: ', data['time_up'])
            print(f"Response: {res}")
            if 'post_id' in res and res['post_id']:
                if 'id' in his:
                    self.history_instance.update_count(his['id'], {'type': 'success'})
                if newfeedid != 0:
                    newfeed_instance.update(newfeedid,{'post_id': res['post_id'],'status': 3})
            else:
                if newfeedid != 0:
                    newfeed_instance.update(newfeedid,{'status': 4})
            
            print("=> Đã lưu thành công!")
            print("\n-----------------------------------------------------\n")
            
        except Exception as e:
            print(e)
            raise e


    def updateStatusAcount(self,status):
        # 1: Lỗi cookie,
        # 2: Đang hoạt động,
        # 3: Đang lấy dữ liệu...,
        # 4: Đang đăng bài...
        self.account_instance.update_account(self.account['id'], {'status_login': status})
        
    def updateStatusAcountCookie(self,cookie_id, status):
        # 1: Chết cookie
        # 2: Cookie đang sống
        self.account_cookies.update(cookie_id,{'status': status})
        
    def updateStatusHistory(self, history_id, status):
        return self.history_crawl_page_post_instance.update(history_id, {'status': status})