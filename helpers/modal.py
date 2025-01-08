from selenium.webdriver.common.by import By

def closeModal(index, browser,last = False):
    try:
        closeModels = browser.find_elements(By.XPATH, '//*[@aria-label="Close"]')
        # validModels = [
        #     model for model in closeModels 
        #     if model.is_displayed() 
        #     and model.is_enabled() 
        #     and model.size['width'] > 0 
        #     and model.size['height'] > 0
        # ]

        if len(closeModels) > index:
            if last:
                closeModels[-1].click()
            else:
                closeModels[index].click()
        else:
            print("Không tìm thấy phần tử hợp lệ tại index:", index)
    except Exception as e:
        print("Lỗi:", str(e))