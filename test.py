# from helpers.time import convert_to_db_format

# time_strings = ["13h"]
# import re
# # In kết quả
# for original in time_strings:   
#     cleaned_text = re.sub(r'[^a-zA-Z0-9 ]', '', original)
#     converted = convert_to_db_format(cleaned_text)
#     print(f"Original: {original} -> Converted for DB: {converted}")


# from facebook.crawl import Crawl
# from base.browser import Browser
# import json
# from time import sleep
# manager = Browser()
# browser = manager.start(False)
# browser.get("https://www.facebook.com/phoenixrisingandsthriving/posts/pfbid0cn9ob8eMqZkNFwiAr4iPo1ojfobeYgML9sd35wV757puKZPH15JCqKsfhdPxwu9Dl?amp%3B__tn__=%2CO%2CP-R")
# sleep(2)
# crawl = Crawl(browser)
# data = crawl.crawlContentPost({}, {
#     'id': 'pfbid0cn9ob8eMqZkNFwiAr4iPo1ojfobeYgML9sd35wV757puKZPH15JCqKsfhdPxwu9Dl',
#     'link': 'https://www.facebook.com/phoenixrisingandsthriving/posts/pfbid0cn9ob8eMqZkNFwiAr4iPo1ojfobeYgML9sd35wV757puKZPH15JCqKsfhdPxwu9Dl?amp%3B__tn__=%2CO%2CP-R',
# }, {}, newfeed = True)

# crawl.likePost()

# # print(json.dumps(data,indent=4))

# sleep(1000)

# Đăng bài
# from base.browser import Browser
# from time import sleep
# from extensions.auth_proxy import create_proxy_extension
# from selenium.webdriver.common.by import By
# import requests
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# import os

# from sql.accounts import Account
# import json
# account_instance = Account()
# acc = account_instance.find(77)
# extension = create_proxy_extension(acc.get('proxy'))
# manager = Browser('/test',extension,'edge',False,True)
# driver = manager.start(False)

# user = "0333026322"
# pwd = "@Zthuong1994"

# driver.get('https://facebook.com/login')
# sleep(5)
# try:
#     driver.find_element(By.ID,'email').send_keys(user)
#     sleep(1)
#     driver.find_element(By.ID,'pass').send_keys(pwd)
#     sleep(1)
#     driver.find_element(By.NAME,'login').click()
#     sleep(10)
# except:
#     pass

# driver.get('https://facebook.com/profile')
# sleep(3000)
# text = "What's on your mind?"
# yourThink = driver.find_element(By.XPATH,f'//*[text()="{text}"]')
# yourThink.click()
# import uuid

# sleep(3)
# input_element = driver.switch_to.active_element
# input_element.send_keys('Xin chào các bạn')

# form = input_element.find_element(By.XPATH,'./ancestor::form')

# # Hàm tải ảnh về
# def download_image(url, temp_dir="./images", temp_file="image.png"):
#     os.makedirs(temp_dir, exist_ok=True)  # Tạo thư mục tạm nếu chưa có
#     temp_path = os.path.join(temp_dir, temp_file)
#     response = requests.get(url)
#     if response.status_code == 200:
#         with open(temp_path, 'wb') as file:
#             file.write(response.content)
#         return os.path.abspath(temp_path)
#     else:
#         raise Exception(f"Không thể tải ảnh từ {url}")

# # Hàm xóa file sau khi dùng xong
# def delete_image(file_path):
#     if os.path.exists(file_path):
#         os.remove(file_path)


# images = [
#     'https://scontent-msp1-1.xx.fbcdn.net/v/t39.30808-6/473052870_630803815965318_4867811670978317300_n.jpg?stp=dst-jpg_s640x640_tt6&_nc_cat=101&ccb=1-7&_nc_sid=127cfc&_nc_ohc=4DiKJBKIJh0Q7kNvgERtSyP&_nc_zt=23&_nc_ht=scontent-msp1-1.xx&_nc_gid=A5fMgxIc0VzDgAvZUMKP9SE&oh=00_AYCY01AeglrWOODkf4vWsNO0S5QPsU9NtYz0TrI51jZ-FQ&oe=6785CB8E',
#     'https://external-msp1-1.xx.fbcdn.net/emg1/v/t13/10722497893744607031?url=https%3A%2F%2Fimages.complex.com%2Fcomplex%2Fimage%2Fupload%2Far_1.91%2Cc_fill%2Cg_auto%2Cq_auto%2Cw_1200%2Fv1736351127%2Fboosie-liangelo-ball_bkj8um&fb_obo=1&utld=complex.com&stp=c0.5000x0.5000f_dst-jpg_flffffff_p500x261_q75_tt6&ccb=13-1&oh=06_Q399rUbhJbYuaS-XeHYn6t557hGgWhXZDw37z3_oHXYSsOc&oe=67818791&_nc_sid=c97757'
# ]

# # Xử lý từng ảnh
# for i, url in enumerate(images):
#     photo_video_element = form.find_element(By.XPATH, './/div[@aria-label="Photo/video"]')
#     photo_video_element.click()
#     listLinkTemps = []
#     try:
#         # Bước 1: Tải ảnh về
#         temp_image_path = download_image(url, temp_file=f"image_{i}_{uuid.uuid4()}.png")
#         listLinkTemps.append(temp_image_path)

#         # Bước 2: Tìm thẻ input và gửi file
#         file_input = driver.find_elements(By.XPATH, '//input[@type="file"]')[-1]
#         file_input.send_keys(temp_image_path)

#         sleep(3)  # Chờ ảnh được tải lên hoàn toàn
#     except Exception as e:
#         print(f"Lỗi khi tải hoặc upload ảnh: {e}")
#     finally:
#         for file in listLinkTemps:
#             # Bước 3: Xóa file tạm sau khi gửi
#             delete_image(temp_image_path)

# form.submit()
# sleep(10)
# print("Đăng bài thành công")
# driver.quit()




from PIL import Image
import pytesseract

# Đảm bảo Tesseract có đường dẫn đúng (trong trường hợp sử dụng Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Cập nhật đường dẫn nếu cần

def solve_captcha(image_path):
    # Mở hình ảnh CAPTCHA
    image = Image.open(image_path)
    
    # Dùng Tesseract để nhận diện văn bản từ hình ảnh
    captcha_text = pytesseract.image_to_string(image, config='--psm 6')  # Cấu hình psm 6 cho OCR
    
    # Làm sạch văn bản đầu ra
    captcha_text = captcha_text.strip()  # Xóa khoảng trắng thừa hoặc ký tự không cần thiết
    
    return captcha_text

# Đọc và giải mã CAPTCHA từ file
image_path = "captcha.png"  # Đường dẫn đến file CAPTCHA
captcha_result = solve_captcha(image_path)

print(f"Captcha đã giải mã: {captcha_result}")
