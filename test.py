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

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep


chrome_options = Options()
chrome_options.add_extension("extensions/62_164_255_151.zip")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://whatismyipaddress.com")
sleep(1000)
driver.quit()


