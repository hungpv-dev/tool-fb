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
from selenium.webdriver.common.by import By

def clickText(driver,text):
    driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]").click()
    

manager = Browser('/hung',None,'edge')
driver = manager.start(False)
driver.get("https://facebook.com")
sleep(1)
pwdMail = "EP69rcdPQ5"
mail = "starowitzshm702517@hotmail.com"
user = "100015926137182"
pwd = "A@!Aurae"

driver.find_element(By.ID,'email').send_keys(user)
driver.find_element(By.ID,'pass').send_keys(pwd)

driver.find_element(By.NAME,'login').click()

sleep(10000)

clickText(driver,'Try another way')

sleep(5)

clickText(driver,'Email')

sleep(2)

clickText(driver,'Continue')

sleep(3)

driver.execute_script("window.open('https://outlook.office.com/login','_blank')")
driver.switch_to.window(driver.window_handles[1])

sleep(5)

driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(mail)
driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()

sleep(5)

driver.find_element(By.CSS_SELECTOR,'input[type="password"]').send_keys(pwdMail)
driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()

sleep(5)

from selenium.common.exceptions import NoSuchElementException
try:
    driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()
except NoSuchElementException as e:
    print("Không cần chuyển tiếp")

sleep(5)

messages = driver.find_elements(By.XPATH, '//*[@aria-posinset]')
for mess in messages:
    try:
        facebook_element = mess.find_element(By.XPATH, './/*[@aria-label="Facebook"]')
        facebook_element.click()
        break
    except NoSuchElementException:
        print("Không phải thẻ có thuộc tính facebook")

sleep(3)

import re

code = None
spans = driver.find_elements(By.XPATH, '//span')
for span in spans:
    span_text = span.text.strip()
    if re.match(r'^\d+$', span_text):  
        code = span_text

if code:
    handles = driver.window_handles
    # driver.close()
    driver.switch_to.window(handles[0])
    driver.find_element(By.NAME,'email').send_keys(code)
    clickText(driver,'Continue')

sleep(10000)
driver.quit()
