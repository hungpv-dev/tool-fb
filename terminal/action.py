from sql.accounts import Account
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from base.browser import Browser
from crawl import crawl
import os
from extensions.auth_proxy import create_proxy_extension
from push import push
from time import sleep
from facebook.login import HandleLogin
from helpers.inp import selected_proxy
from facebook.helpers import login as loginfacebook
from helpers.inp import check_proxy
from newsfeed import newsfeed as newfeedhandle
import shutil

account = Account()
console = Console()

def fanpage():
    tab_question = inquirer.Text('countTab', message="Nhập số tab sẽ mở", default="")
    tab_answer = inquirer.prompt([tab_question])
    countTab = max(1, int(tab_answer['countTab']))
    crawl(countTab)

def post():
    accounts = account.get_accounts({'typenot': 1})['data']
    accounts_question = inquirer.Checkbox('accounts', message="Chọn tài khoản:", choices=[account['name'] for account in accounts], default=[])
    accounts_answers = inquirer.prompt([accounts_question])

    selectAccount = accounts_answers['accounts']
    if len(selectAccount) > 0:
        selected_account_ids = [account['id'] for account in accounts if account['name'] in accounts_answers['accounts']]
        console.print(f"[bold yellow]Tài khoản đã chọn:[/] [bold cyan]{', '.join(selectAccount)}[/]")
        push(selected_account_ids)
    else:
        console.print("Bạn đã không chọn tài khoản.")

def newsfeed():
    accounts = account.get_accounts({'typenot': 2})['data']
    accounts_question = inquirer.Checkbox('accounts', message="Chọn tài khoản:", choices=[account['name'] for account in accounts], default=[])
    accounts_answers = inquirer.prompt([accounts_question])

    selectAccount = accounts_answers['accounts']
    if len(selectAccount) > 0:
        selected_account_ids = [account['id'] for account in accounts if account['name'] in accounts_answers['accounts']]
        console.print(f"[bold yellow]Tài khoản đã chọn:[/] [bold cyan]{', '.join(selectAccount)}[/]")
        newfeedhandle(selected_account_ids)
    else:
        console.print("Bạn đã không chọn tài khoản.")

def login():
    accounts = account.get_accounts()['data']
    accounts_question = inquirer.List('accounts', 
                                     message="Chọn tài khoản:", 
                                     choices=[account['name'] for account in accounts], 
                                     default=None) 
    accounts_answers = inquirer.prompt([accounts_question])

    selectAccount = accounts_answers['accounts']
    if selectAccount:
        console.print(f"[bold yellow]Tài khoản đã chọn:[/] [bold cyan]{selectAccount}[/]")
        try:
            selected_account = next(account for account in accounts if account['name'] == selectAccount)
            checkProxy = True
            extension = None
            proxy = selected_account.get('proxy')
            if proxy:
                checkProxy = check_proxy(proxy)
                if checkProxy :
                    extension = create_proxy_extension(proxy)
            if checkProxy:
                fullpath = os.path.abspath(f'./profiles/login')
                if os.path.exists(fullpath):
                    shutil.rmtree(fullpath,ignore_errors=True)  

                manager = Browser('/login',extension,'chrome',False,True)
                browser = manager.start(False)
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC


                try:
                    login = HandleLogin(browser,selected_account)
                    login.loginFacebook()
                except:
                    raise ValueError('Không login được')
                
                WebDriverWait(browser, 600).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Your profile"]'))
                )
                login.saveLogin()
                sleep(99999999)
            else:
               console.print(f"[bold red]Không dùng được proxy :[/] [bold cyan]{proxy['ip']}:{proxy['port']}[/]")
        except Exception as e:
            print(e)        
            console.print(f"[bold red]Đăng nhập thất bại :[/] [bold cyan]{selectAccount}[/]")
    else:
        console.print("Bạn đã không chọn tài khoản.")