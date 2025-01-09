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

from base.browser import Browser
from time import sleep
from extensions.auth_proxy import create_proxy_extension
from selenium.webdriver.common.by import By

from sql.accounts import Account
import json
account_instance = Account()
acc = account_instance.find(77)
extension = create_proxy_extension(acc.get('proxy'))
manager = Browser('/test',extension)
driver = manager.start(False)
from facebook.login import HandleLogin

login = HandleLogin(driver,acc)

try:
    login.loginFacebook()
except Exception as e:
    print('Login thất bại rồi, :(())')

sleep(10000)
driver.quit()

# pwdMail = "E70cnyLU8"
# mail = "engelbachecy942525@hotmail.com"
# user = "100025302769856"
# pwd = "A@!Aurae"

