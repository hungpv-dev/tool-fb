from selenium.webdriver.common.by import By

def closeModal(index, browser,last = False):
    try:
        closeModels = browser.find_elements(By.XPATH, '//*[@aria-label="Close"]')

        if len(closeModels) > index:
            if last:
                closeModels[-1].click()
            else:
                closeModels[index].click()
        else:
            print("Không tìm thấy phần tử hợp lệ tại index:", index)
    except Exception as e:
        print("Lỗi:", str(e))