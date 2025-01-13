
from tools.types import types,removeString,removeDyamic,selectDyamic,removeComment
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import re
from helpers.time import convert_to_db_format
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException,ElementClickInterceptedException
import random
from sql.posts import Post
from helpers.modal import closeModal
from helpers.fb import clean_url_keep_params
from sql.pages import Page
from sql.errors import Error
from sql.history import HistoryCrawlPage
from sql.accounts import Account
from sql.account_cookies import AccountCookies
from sql.comment import Comment 

class CrawlContentPost:
    def __init__(self, browser):
        self.browser = browser
        self.page_instance = Page()
        self.history_instance = HistoryCrawlPage()
        self.post_instance = Post()
        self.comment_instance = Comment()
        self.error_instance = Error()
        self.account_instance = Account()
        self.account_cookies = AccountCookies()
        self.modal = None

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
        from helpers.fb import is_valid_link
        data = {
            'account_id': post.get('account_id') or 0,
            'cookie_id': post.get('cookie_id') or 0,
            'link_facebook': clean_url_keep_params(post["link"]),
            'post_id': post["id"],
            'page_id': page.get('id') or 0,
            'history_id': his.get('id') or 0,
            'newfeed': post.get('newfeed') or 0,
            'media' : {
                'images': [],
                'videos': []
            },
            'up': 0,
        }
        dataComment = []
        sleep(2)
        print(f"Bắt đầu lấy dữ liệu bài viết")
        
        modal = None # Xử lý lấy ô bài viết
        for modalXPath in types['modal']:
            try:
                print(f'****:  {modalXPath}')
                modal = self.browser.find_element(By.XPATH, modalXPath)
                break
            except Exception as e:
                continue

        if not modal:
            print('Không tìm thấy modal')
            raise ValueError('Không tìm thấy modal')        
        else:
            aria_posinset = modal.get_attribute("aria-posinset")
            if aria_posinset is None:
                closeModal(2, self.browser)
            else:
                print(post['link'])
                closeModal(0, self.browser)

        timeUp = None

        try:
            linkTimeUp = WebDriverWait(modal, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//a[@attributionsrc]"))
            )
            if linkTimeUp and len(linkTimeUp) > 0:
                for link in linkTimeUp:
                    try:
                        rect = link.rect
                        if rect['width'] > 0 and rect['height'] > 0:
                            # Xử lý text của thẻ
                            href_text = link.text.strip()
                            cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', href_text)
                            formatted_time = convert_to_db_format(cleaned_text)
                            if formatted_time:
                                timeUp = formatted_time
                    except StaleElementReferenceException:
                        print("Element no longer in the DOM, retrying...")
                        sleep(1)
                        continue
        except StaleElementReferenceException:
            print("The element is stale and cannot be accessed.")
        
        data['time_up'] = timeUp

        self.modal = modal

        data['content'] = extract_facebook_content(modal)

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
            print(f"Không lấy được like, comment, share")
        # Lấy comment
        try:
            scroll = modal.find_element(By.XPATH,types['scroll'])
            self.browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll)
            print('Cuộn chuột xuống')
        except: 
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        
        try:
            comments = modal.find_elements(By.XPATH, types['comments'])
            
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
        
    def likePost(self):
        try:
            scroll = self.modal.find_element(By.XPATH,types['scroll'])
            self.browser.execute_script("arguments[0].scrollTop = 0;", scroll)
        except: 
            self.browser.execute_script("window.scrollTo(0, 0);")
        # # Tìm thẻ có aria-label="Like"
        # self.browser.execute_script("document.body.style.zoom='50%';")
        icon = ""
        sleep(2)
        try:
            like_element = self.modal.find_element(By.XPATH, './/*[@data-ad-rendering-role="like_button"]')
            ActionChains(self.browser).move_to_element(like_element).perform()
            sleep(1)
            parents_icons = self.browser.find_elements(By.XPATH,'.//*[@data-visualcompletion="ignore-dynamic"]')[-1]
            labels = ['Love','Like','Care','Haha','Wow','Sad','Angry']

            eles = []
            if parents_icons:
                for label in labels:
                    try:
                        ele = parents_icons.find_element(By.XPATH,f'.//*[@aria-label="{label}"]')
                        eles.append(ele)
                    except NoSuchElementException as e:
                        print(f"Không có icon: {label}")
            
            if len(eles) > 0:
                clicked = False
                while eles and not clicked:
                    ele = random.choice(eles)  
                    try:
                        icon = ele.get_attribute("aria-label")
                        ele.click()
                        clicked = True 
                        sleep(1)
                        break
                    except ElementClickInterceptedException as e:
                        icon = ""
                        print("Không thể nhấp vào phần tử, thử phần tử khác.")
                        eles.remove(ele)
                if not clicked:
                    try:
                        like_element.click()
                        icon = "Like"
                    except Exception as e:
                        pass
            else:
                print("Không có phần tử nào khả dụng.")
        except Exception as e:
            print(e)
            print("Không tìm thấy thẻ like!")
        return icon
        
    def viewImages(self, post):
        try:
            media = post.get('media')
            if media and 'images' in media:
                images = media.get('images', [])
                for img in images:
                    try:
                        if isinstance(img, str): 
                            self.browser.get(img)
                        else:
                            print(f"URL không hợp lệ: {img}")
                    except Exception as e:
                        print(f"Lỗi khi truy cập hình ảnh {img}: {e}")
                    sleep(5)
        except Exception as e:
            print(f"Lỗi khi xem hình ảnh: {e}")

    def insertPostAndComment(self, data, dataComment, his, newfeedid = 0):
        
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
                    newfeed_instance.destroy(newfeedid)
            
            print("=> Đã lưu thành công!")
            print("\n-----------------------------------------------------\n")
            
        except Exception as e:
            print(e)
            raise e


def extract_facebook_content(modal):
    try:
        content = modal.find_element(By.XPATH, types['content'])
        contentText = content.text
        for string in removeString:
            contentText = contentText.replace(string, '')
        return contentText.strip()
    except Exception as e:
        print(f'Không tìm thấy nội dung')
        return ''