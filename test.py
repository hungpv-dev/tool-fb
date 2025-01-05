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

proxy = {
    'ip': '207.228.20.5',
    'port': '45774',
    'user': 'SszaLu98T4t2h4S',
    'pass': '703sNOIwSCHa1Wg',
}

manager = Browser('/hung',proxy)
driver = manager.start(False)
driver.get("https://whatismyipaddress.com")
sleep(10)
driver.quit()



# # Khởi tạo options cho Firefox
# options = FirefoxOptions()

# # Khởi tạo WebDriver với selenium-wire


# # Khởi tạo Firefox WebDriver với cấu hình selenium-wire và proxy
# driver = webdriver.Firefox(
#     service=FirefoxService(GeckoDriverManager().install()),
#     options=options,
#     seleniumwire_options=seleniumwire_options
# )



