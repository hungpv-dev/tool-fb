from time import sleep
from tools.types import push
from selenium.webdriver.common.by import By
from sql.accounts import Account
from helpers.modal import clickOk
import logging
import re
from bot import send
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from captcha import Captcha

captcha_instance = Captcha()

class HandleLogin:
    def __init__(self,driver,acc,main_model = None):
        self.driver = driver
        self.account_instance = Account()
        self.account = acc
        self.main_model = main_model

    def getAccount(self):
        return self.account
    
    def setAccount(self):
        account = self.account_instance.find(self.account.get('id'))
        self.email = self.account.get('email_account')
        self.pwdEmail = self.account.get('email_password')
        self.user = self.account.get('login_account')
        self.pwd = self.account.get('login_password')
        self.account = account

    def updateMainModel(self,text):
        if self.main_model:
            self.main_model.update_process(self.account.get('id'),text)
    

    def loginFacebook(self,sendNoti = True):
        self.sendNoti = sendNoti
        self.setAccount()
        try:
            logging.info(f"Bắt đầu thực khi login: {self.account.get('name')}")
            print(f"Bắt đầu thực khi login: {self.account.get('name')}")
            self.driver.get("https://facebook.com")
            sleep(3)
            clickOk(self.driver)

            self.saveAlowCookie()
            
            try:
                self.updateMainModel('Login với cookie')
                self.login()
            except Exception as e:
                self.updateMainModel('Không thể login với cookie')
                pass

            self.saveAlowCookie()
            check = self.saveLogin(False)
            sleep(2)
            if check == False:
                self.driver.get("https://facebook.com/login")
                sleep(3)
                self.driver.find_element(By.ID,'email').send_keys(self.user)
                sleep(1)
                self.driver.find_element(By.ID,'pass').send_keys(self.pwd)
                sleep(1)
                try:
                    self.driver.find_element(By.NAME,'login').click()
                except: 
                    self.driver.find_element(By.ID,'loginbutton').click()
                sleep(5)
                self.saveAlowCookie()

                self.handleCaptcha()

                self.updateMainModel('Login với username, password')
                check = self.saveLogin()
                if check == False:
                    try:
                        self.toggleType('Authentication app')
                        authenapp = self.driver.find_element(
                            By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'authentication app')]"
                        )
                        logging.info(f'{self.account.get("name")} lấy mã xác thực App Authenticate')
                        print(f'{self.account.get("name")} lấy mã xác thực App Authenticate')
                        self.updateMainModel('Login với 2fa')
                        authenapp.click()
                        self.clickText('Continue')
                        code = self.getCode2Fa()
                        self.updateMainModel(f'Code là: {code}')
                        check = self.pushCode(code)
                    except NoSuchElementException as e:
                        try:
                            self.driver.find_element(By.NAME,'email')
                            logging.info(f'{self.account.get("name")} lấy mã từ Outlook')
                            print(f'{self.account.get("name")} lấy mã từ Outlook')
                            try:
                                self.updateMainModel('Login với Outlook')
                                self.toggleType('Email') # Chuyển sang nhận mã từ email
                                code = self.loginEmailAndGetCode() # Lấy code
                                self.updateMainModel(f'Code là: {code}')
                                check = self.pushCode(code)
                            except Exception as e:
                                self.account_instance.update_account(self.account.get('id'),{'status_login':1})
                                logging.error(f'{self.account.get("name")} lấy mã từ Audio (chiu)')
                                print(f'{self.account.get("name")} lấy mã từ Audio (chiu)')
                        except Exception as e:
                            pass
        except Exception as e:
            logging.error(f'Lỗi login: {e}')
            print(f'Lỗi login: {e}')
            check = False
        return check

    def handleCaptcha(self):
        try:
            print('Lấy capcha xử lý')
            img_elements = WebDriverWait(self.driver,5).until(
                EC.presence_of_all_elements_located((By.XPATH,'//img[@referrerpolicy="origin-when-cross-origin"]'))
            )
            src = ''
            for img in img_elements:
                captcha_url = img.get_attribute("src")
                if 'captcha' in captcha_url:
                    src = captcha_url
                    break

            if src == '':
                raise ValueError('Khôgn tìm thấy img captcha')
            
            send(f'{self.account.get("name")} bắt đầu xử lý captcha để đăng nhập')
            code = captcha_instance.getCode(src)
            send(f'{self.account.get("name")} lấy từ captchat: {code}')
            self.pushCode(code)
        except Exception as e:
            print('Lỗi khi xử lý captcha')
            print(e)
            logging.error(e)


    def saveAlowCookie(self):
        try:
            print('Chấp nhận tất cả cookie')
            allow_cookies_buttons = WebDriverWait(self.driver,5).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@aria-label="Allow all cookies"]'))
            )
            if len(allow_cookies_buttons) > 1:
                allow_cookies_buttons[-1].click()
            sleep(2)
        except Exception as e:
            pass
        
    def getCode2Fa(self):
        logging.info(f'{self.account.get("name")} Mở web lấy mã')
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

    def toggleType(self,type):
        self.clickText('Try another way')
        sleep(2)
        self.clickText(type)
        sleep(2)
        self.clickText('Continue')
        sleep(5)

    def loginEmailAndGetCode(self):
        logging.info(f'{self.account.get("name")} Mờ outlook')
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
        #     logging.info("Không cần chuyển tiếp")
        #     print("Không cần chuyển tiếp")

        try:
            self.driver.find_element(By.CSS_SELECTOR,'[type="submit"]').click()
        except NoSuchElementException as e:
            logging.error("Không cần chuyển tiếp")
            print("Không cần chuyển tiếp")

        sleep(5)
        logging.info(f'{self.account.get("name")} Đăng nhập outlook thành công, mở inbox')
        print(f'{self.account.get("name")} Đăng nhập outlook thành công, mở inbox')

        self.clickText('Inbox')
        
        sleep(60)
        self.driver.refresh()
        sleep(10)
        return self.getCode()

    def getCode(self):
        logging.info(f'{self.account.get("name")} Lấy code từ outlook')
        print(f'{self.account.get("name")} Lấy code từ outlook')

        messages = self.driver.find_elements(By.XPATH, '//*[@aria-posinset]')
        for mess in messages:
            try:
                facebook_element = mess.find_element(By.XPATH, './/*[@aria-label="Facebook"]')
                facebook_element.click()
                break
            except NoSuchElementException:
                logging.error("Không phải thẻ có thuộc tính facebook")
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
        logging.info(f'{self.account.get("name")} Code là {code}')
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

            sleep(5)
            try:
                self.clickText('Dismiss')
            except:
                pass
            sleep(5)
        else:
            logging.error('Không tìm thấy mã code')
            print('Không tìm thấy mã code')
        sleep(5)
        return self.saveLogin()

    def checkCurrent(self):
        self.driver.get('https://facebook.com')
        sleep(3)
        check = False
        try:
            self.driver.find_element(By.XPATH, push['openProfile'])
            check = True
        except Exception:
            logging.error('Login thất bại, tôi thất bại rồi!')
            print('Login thất bại, tôi thất bại rồi!')
        return check


    def saveLogin(self,saveCookie = True):
        check = False
        try:
            checkBlock = self.checkBlock()
            if checkBlock:
                if self.sendNoti:
                    send(f"Tài khoản: {self.account.get('name')} đã bị khoá")
                self.updateMainModel('Tài khoản đã bị khoá!')
                self.account_instance.update_account(self.account.get('id'),{'status_login': 5})
                return check

            sleep(2)
            clickOk(self.driver)

            self.driver.find_element(By.XPATH, push['openProfile'])
            cookies = self.driver.get_cookies()
            dataUpdate = {
                'status_login': 2
            }
            if saveCookie:
                dataUpdate['cookie'] = cookies
                dataUpdate['type_edit'] = 2

            sleep(1)
            res = self.account_instance.update_account(self.account.get('id'),dataUpdate)
            check = True
            self.updateMainModel(f'Login thành công!')
        except Exception as e:
            self.account_instance.update_account(self.account.get('id'),{'status_login':1})
        return check
    
    def checkBlock(self):
        clickOk(self.driver)
        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), 'your account has been locked')]")
            print('your account has been locked')
            return True
        except NoSuchElementException:
            pass
        
        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), 'Account locked')]")
            print('Account locked')
            return True
        except NoSuchElementException:
            pass

        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), 'You’re Temporarily Blocked')]")
            print('You’re Temporarily Blocked')
            return True
        except NoSuchElementException:
            pass

        return False



    def clickText(self,text):
        try:
            element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            element.click()
        except NoSuchElementException as e:
            logging.error('No has element')
            print('No has element')

    def login(self):
        account = self.account
        try:
            if 'latest_cookie' not in account:
                raise ValueError("Không có cookie để đăng nhập.")
            
            last_cookie = account['latest_cookie']
            
            if 'cookies' not in last_cookie:
                raise ValueError("Không có thông tin cookies trong latest_cookie.")
            
            cookies = last_cookie['cookies']

            if not isinstance(cookies, list):
                raise ValueError("Dữ liệu cookies không hợp lệ. Nó phải là một danh sách.")

            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    raise ValueError(f"Không thể thêm cookie {cookie} vào trình duyệt: {e}")
            
            sleep(1)
            self.driver.get('https://facebook.com')
            sleep(1)

        except Exception as e:
            self.updateMainModel('Không thể login')
            logging.error(f"Lỗi login {account.get('name')}: {e}")
            print(f"Lỗi login {account.get('name')}: {e}")
            if 'latest_cookie' in account and 'id' in account['latest_cookie']:
                self.updateStatusAcountCookie(account['latest_cookie']['id'], 1)
        
    def updateStatusAcountCookie(self,cookie_id, status):
        # 1: Chết cookie
        # 2: Cookie đang sống
        from sql.account_cookies import AccountCookies
        account_cookies = AccountCookies()
        account_cookies.update(cookie_id,{'status': status})

    def updateStatusAcount(self,account_id, status):
        # 1: Lỗi cookie,
        # 2: Đang hoạt động,
        # 3: Đang lấy dữ liệu...,
        # 4: Đang đăng bài...
        account_instance = Account()
        account_instance.update_account(account_id, {'status_login': status})
            

