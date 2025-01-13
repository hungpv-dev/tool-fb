from tools.facebooks.browser_post import Push
from tools.driver import Browser
from helpers.image import delete_image,download_image
from time import sleep
from extensions.auth_proxy import create_proxy_extension
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
from sql.accounts import Account
from helpers.login import HandleLogin
account_instance = Account()
import uuid
from helpers.modal import closeModal
import json
from tools.facebooks.crawl_content_post import CrawlContentPost



class Test:
    def post(self,id):
        acc = account_instance.find(id)
        if not acc: return

        extension = create_proxy_extension(acc.get('proxy'))
        manager = Browser(f'/test/{id}',extension,loadContent=True)
        driver = manager.start(False)
        sleep(3)

        loginInstance = HandleLogin(driver,acc)
        checkLogin = loginInstance.loginFacebook()
        if checkLogin == False: return
        push_instance = Push(driver,acc,extension,manager)
        driver.get('https://facebook.com/profile')
        sleep(3)
        text = "What's on your mind?"
        yourThink = driver.find_element(By.XPATH,f'//*[text()="{text}"]')
        yourThink.click()
        sleep(3)
        input_element = driver.switch_to.active_element
        input_element.send_keys('Xin chào các bạn')

        form = input_element.find_element(By.XPATH,'./ancestor::form')

        images = [
            'https://scontent-msp1-1.xx.fbcdn.net/v/t39.30808-6/473052870_630803815965318_4867811670978317300_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_ohc=4DiKJBKIJh0Q7kNvgERtSyP&_nc_zt=23&_nc_ht=scontent-msp1-1.xx&_nc_gid=A5fMgxIc0VzDgAvZUMKP9SE&oh=00_AYCY01AeglrWOODkf4vWsNO0S5QPsU9NtYz0TrI51jZ-FQ&oe=6785CB8E',
            'https://scontent-msp1-1.xx.fbcdn.net/v/t39.30808-6/473052870_630803815965318_4867811670978317300_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_ohc=4DiKJBKIJh0Q7kNvgERtSyP&_nc_zt=23&_nc_ht=scontent-msp1-1.xx&_nc_gid=A5fMgxIc0VzDgAvZUMKP9SE&oh=00_AYCY01AeglrWOODkf4vWsNO0S5QPsU9NtYz0TrI51jZ-FQ&oe=6785CB8E'
        ]

        # Xử lý từng ảnh
        for i, url in enumerate(images):
            photo_video_element = form.find_element(By.XPATH, './/div[@aria-label="Photo/video"]')
            photo_video_element.click()
            listLinkTemps = []
            try:
                # Bước 1: Tải ảnh về
                temp_image_path = download_image(url, temp_file=f"image_{i}_{uuid.uuid4()}.png")
                listLinkTemps.append(temp_image_path)
                sleep(3)

                # Bước 2: Tìm thẻ input và gửi file
                file_input = form.find_elements(By.XPATH, './/input[@type="file"]')[-1]
                file_input.send_keys(temp_image_path)

                sleep(3)  # Chờ ảnh được tải lên hoàn toàn
            except Exception as e:
                print(f"Lỗi khi tải hoặc upload ảnh: {e}")

        form.submit()
        sleep(10000)
        for file in listLinkTemps:
            # Bước 3: Xóa file tạm sau khi gửi
            delete_image(temp_image_path)
        print("Đăng bài thành công")
        driver.quit()
    
    def crawl(self,id):
        acc = account_instance.find(id)
        if not acc: return
        extension = create_proxy_extension(acc.get('proxy'))
        manager = Browser(f'/test/{id}',extension,loadContent=True)
        driver = manager.start(False)
        sleep(3)
        loginInstance = HandleLogin(driver,acc)
        checkLogin = loginInstance.loginFacebook()
        if checkLogin == False: return
        crawl_instance = CrawlContentPost(driver)
        up = {
            'id': '10161000087849142',
            'link': 'https://www.facebook.com/FailBlog/posts/1013999034094119',
        }
        driver.get(up['link'])
        sleep(1)
        data = crawl_instance.crawlContentPost({},up,{},True)
        icon = crawl_instance.likePost()
        data.get('post')['icon'] = icon
        crawl_instance.viewImages(data.get('post'))
        print(json.dumps(data,indent=4))
        sleep(100000)
        driver.quit()



# # Đăng bài
# test = Test()
# # test.post(78)
# test.crawl(75)

# href = 'https://www.facebook.com/permalink.php?story_fbid=534717943055769&amp%3Bid=100095527030131'
# href = 'https://www.facebook.com/permalink.php?story_fbid=122172726248280714&amp%3Bid=61558421431250'
# from helpers.fb import clean_url_keep_params
# print(clean_url_keep_params(href))






