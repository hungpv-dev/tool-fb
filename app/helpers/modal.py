from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
def closeModal(index, browser,last = False):
    try:
        closeModels = browser.find_elements(By.XPATH, '//*[@aria-label="Close"]')

        if len(closeModels) > index:
            if last:
                closeModels[-1].click()
            else:
                closeModels[index].click()
        else:
            logging.error(f"Không tìm thấy phần tử hợp lệ tại index: {index}")
            print(f"Không tìm thấy phần tử hợp lệ tại index: {index}")
    except Exception as e:
        logging.error(f"Lỗi: {str(e)}")
        print(f"Lỗi: {str(e)}")

def openProfile(browser,name_fanpage = ''):
    from tools.types import push
    try:
        # Chờ tối đa 10 giây để `profile_button` xuất hiện
        profile_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, push['openProfile']))
        )
        profile_button.click()

        # Chờ tối đa 10 giây để `allFanPage` xuất hiện
        try:
            allFanPage = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, push['allProfile']))
            )
            allFanPage.click()
        except Exception as e:
            pass
    except Exception as e:
        raise e

    sleep(10)
    allPages = browser.find_elements(By.XPATH, '//*[@aria-label="Your profile" and @role="dialog"]//*[@role="list"]//*[@role="listitem" and @data-visualcompletion="ignore-dynamic"]')
    if len(allPages) > 0:
        allPages = allPages[1:]
        for i, page in enumerate(allPages):
            textPage = page.text
            if "Create new profile" in textPage:
                allPages = allPages[:i]
                break

    else:
        try:
            see_more_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "See more profiles")]'))
            )
            see_more_button.click()  
        except:
            print('See more profiles not found')
        sleep(10)
        allPages = browser.find_elements(By.XPATH, '//*[@role="dialog"]//*[@role="list"]//*[@role="listitem" and @data-visualcompletion="ignore-dynamic"]')
        allPages.pop(0)
    actionsChains = ActionChains(browser)
    if name_fanpage:
        for page in allPages:
            name = remove_notifications(page.text)
            if name_fanpage == name:
                actionsChains.move_to_element(page).perform()
                sleep(1)
                page.click() 
                break
    return allPages


import re
def remove_notifications(text):
    index = text.lower().find("notifications")
    
    if index != -1:
        text = text[:index].strip() 
        text_parts = text.split()
        if text_parts and text_parts[-1].isdigit():
            text_parts = text_parts[:-1]
            text = ' '.join(text_parts)
    return text

def clickOk(driver):
    try:
        ok_button = driver.find_element(By.XPATH, '//*[@aria-label="OK"]')
        ok_button.click()
        sleep(2)
    except Exception as e:
        print('Không có ok')
        pass