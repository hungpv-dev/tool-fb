from time import sleep
from facebook.type import push
from selenium.webdriver.common.by import By
import json
from sql.accounts import Account
import re
from selenium.common.exceptions import NoSuchElementException
class HandleLogin:
    def __init__(self,driver,acc):
        self.driver = driver
        self.account_instance = Account()
        self.account = acc

    def getAccount(self):
        return self.account
    
    def setAccount(self):
        account = self.account_instance.find(self.account.get('id'))
        self.email = self.account.get('email_account')
        self.pwdEmail = self.account.get('email_password')
        self.user = self.account.get('login_account')
        self.pwd = self.account.get('login_password')
        self.account = account
    

    def loginFacebook(self):
        self.setAccount()
        try:
            from facebook.helpers import login
            print(f"Bắt đầu thực khi login: {self.account.get('name')}")
            self.driver.get("https://facebook.com")
            sleep(2)

            try:
                allow_cookies_buttons = self.driver.find_elements(By.XPATH, '//*[@aria-label="Allow all cookies"]')
                if len(allow_cookies_buttons) > 1:
                    allow_cookies_buttons[-1].click()
                sleep(2)
            except Exception as e:
                pass
            
            try:
                login(self.driver,self.account)
            except:
                pass

            check = self.saveLogin(False)
            if check == False:
                self.driver.get("https://facebook.com/login")
                self.driver.find_element(By.ID,'email').send_keys(self.user)
                sleep(1)
                self.driver.find_element(By.ID,'pass').send_keys(self.pwd)
                sleep(1)
                self.driver.find_element(By.NAME,'login').click()
                sleep(5)
                check = self.saveLogin()
                if check == False:
                    try:
                        authenapp = self.driver.find_element(
                            By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'authentication app')]"
                        )
                        print(f'{self.account.get("name")} lấy mã xác thực App Authenticate')
                        authenapp.click()
                        self.clickText('Continue')
                        code = self.getCode2Fa()
                        check = self.pushCode(code)
                    except NoSuchElementException as e:
                        try:
                            self.driver.find_element(By.NAME,'email')
                            print(f'{self.account.get("name")} lấy mã từ Outlook')
                            self.toggleEmail() # Chuyển sang nhận mã từ email
                            code = self.loginEmailAndGetCode() # Lấy code
                            check = self.pushCode(code)
                        except:
                            self.account_instance.update_account(self.account.get('id'),{'status_login':1})
                            print(f'{self.account.get("name")} lấy mã từ Audio (chiu)')
                            pass
        except Exception as e:
            print(f'Lỗi login: {e}')
            check = False
        return check

            
        
    def getCode2Fa(self):
        print(f'{self.account.get("name")} Mở web lấy mã')


        self.driver.execute_script("window.open('about:blank', '_blank');")
        sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get("https://2fa.live")
        sleep(5)
        self.driver.find_element(By.ID,'listToken').send_keys(self.account.get('keyword_2fa'))
        sleep(1)
        self.driver.find_element(By.ID,'submit').click()

        sleep(5)
        value = self.driver.find_element(By.ID,'output').get_attribute('value')
        parst = value.split('|')
        code = parst[-1]
        self.backTab()
        return code

    def toggleEmail(self):
        self.clickText('Try another way')
        sleep(2)
        self.clickText('Email')
        sleep(2)
        self.clickText('Continue')
        pass

    def loginEmailAndGetCode(self):
        print(f'{self.account.get("name")} Mờ outlook')
        self.driver.execute_script("window.open('about:blank', '_blank');")
        sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[1])

        self.driver.get('https://outlook.office.com/login')

        sleep(10)

        self.driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(self.email)
        self.driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()

        sleep(5)

        self.driver.find_element(By.CSS_SELECTOR,'input[type="password"]').send_keys(self.pwdEmail)
        self.driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()

        # try:
        #     self.driver.find_element(By.CSS_SELECTOR, '[aria-posinset="1"]').click()
        # except NoSuchElementException as e:
        #     print("Không cần chuyển tiếp")

        try:
            self.driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()
        except NoSuchElementException as e:
            print("Không cần chuyển tiếp")

        sleep(5)
        print(f'{self.account.get("name")} Đăng nhập outlook thành công, mở inbox')

        self.clickText('Inbox')
        
        sleep(60)
        self.driver.refresh()
        sleep(10)
        return self.getCode()

    def getCode(self):
        print(f'{self.account.get("name")} Lấy code từ outlook')

        messages = self.driver.find_elements(By.XPATH, '//*[@aria-posinset]')
        for mess in messages:
            try:
                facebook_element = mess.find_element(By.XPATH, './/*[@aria-label="Facebook"]')
                facebook_element.click()
                break
            except NoSuchElementException:
                print("Không phải thẻ có thuộc tính facebook")
        
        sleep(3)
        code = None
        spans = self.driver.find_elements(By.XPATH, '//span')
        for span in spans:
            span_text = span.text.strip()
            if re.match(r'^\d+$', span_text):  
                code = span_text
        self.backTab()

        return code

    def backTab(self):
        handles = self.driver.window_handles
        current_handle = self.driver.current_window_handle

        # Đóng tab hiện tại
        self.driver.close()

        if current_handle != handles[0]:
            self.driver.switch_to.window(handles[0])
        else:
            if len(handles) > 1:
                self.driver.switch_to.window(handles[1])
        sleep(3)
    
    def pushCode(self,code):
        print(f'{self.account.get("name")} Code là {code}')
        if code:

            try:
                self.driver.find_element(By.NAME,'email').send_keys(code)
            except NoSuchElementException as e:
                pass
            
            try:
                self.driver.find_element(By.CSS_SELECTOR,'input[type="text"]').send_keys(code)
            except NoSuchElementException as e:
                pass

            sleep(2)
            self.clickText('Continue')
            sleep(5)

            nexts = self.driver.find_elements(By.XPATH, f"//*[contains(text(), 'Trust this device')]")
            try:
                for next in nexts:
                    next.click()
            except: 
                pass

            sleep(10)
        else:
            print('Không tìm thấy mã code')
        sleep(10)
        return self.saveLogin()

    def checkCurrent(self):
        self.driver.get('https://facebook.com')
        sleep(3)
        check = False
        try:
            self.driver.find_element(By.XPATH, push['openProfile'])
            check = True
        except Exception:
            print('Login thất bại, tôi thất bại rồi!')
        return check


    def saveLogin(self,saveCookie = True):
        check = False
        try:
            self.driver.find_element(By.XPATH, push['openProfile'])
            cookies = self.driver.get_cookies()
            dataUpdate = {
                'status_login': 2
            }
            if saveCookie:
                dataUpdate['cookie'] = cookies
                dataUpdate['type_edit'] = 2

            res = self.account_instance.update_account(self.account.get('id'),dataUpdate)
            check = True
            print('Login thành công')
        except NoSuchElementException as e:
            self.account_instance.update_account(self.account.get('id'),{'status_login':1})
            print('Login thất bại, tôi thất bại rồi!')
        return check


    def clickText(self,text):
        try:
            element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            element.click()
        except NoSuchElementException as e:
            print('No has element')
            

