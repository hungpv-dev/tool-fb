from selenium.webdriver.common.by import By
import logging
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