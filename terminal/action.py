from sql.accounts import Account
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from base.browser import Browser
from crawl import crawl
from extensions.auth_proxy import create_proxy_extension
from push import push
from time import sleep
from helpers.inp import selected_proxy
from facebook.helpers import login as loginfacebook
from newsfeed import newsfeed as newfeedhandle

account = Account()
console = Console()

def fanpage():
    tab_question = inquirer.Text('countTab', message="Nhập số tab sẽ mở", default="")
    tab_answer = inquirer.prompt([tab_question])
    countTab = max(1, int(tab_answer['countTab']))
    crawl(countTab)

def post():
    accounts = account.get_accounts({'type': 2})['data']
    accounts_question = inquirer.Checkbox('accounts', message="Chọn tài khoản:", choices=[account['name'] for account in accounts], default=[])
    accounts_answers = inquirer.prompt([accounts_question])

    selectAccount = accounts_answers['accounts'];
    if len(selectAccount) > 0:
        selected_account_ids = [account['id'] for account in accounts if account['name'] in accounts_answers['accounts']]
        console.print(f"[bold yellow]Tài khoản đã chọn:[/] [bold cyan]{', '.join(selectAccount)}[/]")
        push(selected_account_ids)
    else:
        console.print("Bạn đã không chọn tài khoản.")

def newsfeed():
    accounts = account.get_accounts({'type': 1})['data']
    accounts_question = inquirer.Checkbox('accounts', message="Chọn tài khoản:", choices=[account['name'] for account in accounts], default=[])
    accounts_answers = inquirer.prompt([accounts_question])

    selectAccount = accounts_answers['accounts']
    if len(selectAccount) > 0:
        selected_account_ids = [account['id'] for account in accounts if account['name'] in accounts_answers['accounts']]
        console.print(f"[bold yellow]Tài khoản đã chọn:[/] [bold cyan]{', '.join(selectAccount)}[/]")
        
        dirextension = None
        selectProxy = selected_proxy()
        if selectProxy is not None:
            dirextension = create_proxy_extension(selectProxy)
            
        newfeedhandle(selected_account_ids,dirextension)
    else:
        console.print("Bạn đã không chọn tài khoản.")
    pass

def login():
    accounts = account.get_accounts()['data']
    accounts_question = inquirer.List('accounts', 
                                     message="Chọn tài khoản:", 
                                     choices=[account['name'] for account in accounts], 
                                     default=None) 
    accounts_answers = inquirer.prompt([accounts_question])

    selectAccount = accounts_answers['accounts']
    if selectAccount:
        manager = Browser()
        browser = manager.start(False)
        browser.get("https://facebook.com")
        console.print(f"[bold yellow]Tài khoản đã chọn:[/] [bold cyan]{selectAccount}[/]")
        try:
            selected_account = next(account for account in accounts if account['name'] == selectAccount)
            loginfacebook(browser,selected_account)
            sleep(99999999)
        except:        
            console.print(f"[bold red]Đăng nhập thất bại :[/] [bold cyan]{selectAccount}[/]")
    else:
        console.print("Bạn đã không chọn tài khoản.")