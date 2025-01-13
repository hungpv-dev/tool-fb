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
            'link': 'https://www.facebook.com/homesoftherich/posts/982177123948005?__cft__[0]=AZUS2xdrxGoD7-RDr_t_JMMMFqfL-SfusGDTXs5Rij_QLdHXYZiHCKjKZLo3zwnaD4EqzWaL2OBQN_oo1kKWi_ReiljxaEYVrfOQcW8WX-_fZ902zHPzuHt8qs7KhnDArdZCXIq07aDa3XAq28VS6R0BTm4TZym9DyXNKujTPw_MUnDlVGre8jQZyn5EdP3-t8c&__tn__=%2CO%2CP-R',
        }
        driver.get(up['link'])
        sleep(1)
        data = crawl_instance.crawlContentPost({},up,{},True)
        sleep(2)
        crawl_instance.shareCopyLink()
        crawl_instance.sharePostAndOpenNotify()
        icon = crawl_instance.likePost()
        data.get('post')['icon'] = icon
        closeModal(2,driver)
        sleep(1)
        crawl_instance.viewImages(data.get('post'))
        print(json.dumps(data,indent=4))
        sleep(100000)
        driver.quit()



# Đăng bài
# test = Test()
# test.post(78)
# test.crawl(75)

# href = 'https://www.facebook.com/homesoftherich/posts/982177123948005?__cft__[0]=AZUS2xdrxGoD7-RDr_t_JMMMFqfL-SfusGDTXs5Rij_QLdHXYZiHCKjKZLo3zwnaD4EqzWaL2OBQN_oo1kKWi_ReiljxaEYVrfOQcW8WX-_fZ902zHPzuHt8qs7KhnDArdZCXIq07aDa3XAq28VS6R0BTm4TZym9DyXNKujTPw_MUnDlVGre8jQZyn5EdP3-t8c&__tn__=%2CO%2CP-R'
from helpers.fb import clean_url_keep_params,clean_facebook_url_redirect
import urllib
hrefs = [
    'https://l.facebook.com/l.php?u=https%3A%2F%2Fhomesoftherich.net%2F%3Fs%3Dgeorgia%26fbclid%3DIwZXh0bgNhZW0CMTAAAR25nlkMk94AcF8f-1GWm6Bd-YwIfBu8ozPBT7LWfj-U6qQn6NMCphzupMs_aem_wZjvYlVwSLGze_h4JJbtBg&h=AT1zb_HiX8nv68-dDEa-4ByzC-7hEHAWVRjhcxDun5oD3PeYFe0khr_D4AyLuBM23uLOe3VaP6pC6CdnYhoc7KPzTr-MdP92c1_YORzniIw4wgJVpw5NcXoNGXaGN4UrDe45D16i_MxY1sXV&__tn__=R]-R&c[0]=AT2tZSWbS7JHY4kmMSyjJjcAHQ7NLpq98h1i4XwYPWq1b7jsysaOi6KZLjrplaPYWekx4FTlyeqUkWKd9i3oERvA1uviVxIdcWQ7cJZBcbW5h5nqCv7Oh0CO3WtP0QcD3W-3HGD8NCF3JG32sFox7EPUNs5cJv76W_qLwKEEZxtWdoHU_hOC2repqn_FYCrN',
    'https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-6/473568457_982177083948009_6456232874414359120_n.jpg?stp=dst-jpg_s600x600_tt6&_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_ohc=CieBVTEu9-UQ7kNvgGX-dJr&_nc_zt=23&_nc_ht=scontent-iad3-1.xx&_nc_gid=ATEHWXeV-oDam1v1EAvLz3Y&oh=00_AYBt2sPTty1ZH6g0j2jBCAlfomTTDIq2boMdlk7ky6DtQQ&oe=678A5D8B',
    'https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-6/473192326_982177077281343_8538946828122243783_n.jpg?stp=dst-jpg_p480x480_tt6&_nc_cat=108&ccb=1-7&_nc_sid=127cfc&_nc_ohc=54op3P1nYcEQ7kNvgFc-wo-&_nc_zt=23&_nc_ht=scontent-iad3-1.xx&_nc_gid=ATEHWXeV-oDam1v1EAvLz3Y&oh=00_AYClC8CHv2VQymbqQQTYgOa2Ap_-1OOmrKCWL1OOciGhyA&oe=678A72FD'
]
for href in hrefs:
    print(clean_facebook_url_redirect(href))






