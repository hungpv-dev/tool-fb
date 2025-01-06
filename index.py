import inquirer
from rich.console import Console
from rich.panel import Panel
import subprocess
from rich.text import Text
import warnings
from helpers.inp import periodic_cleanup
from terminal.action import post,newsfeed,fanpage,login

warnings.filterwarnings("ignore", message="Old MapAsync APIs are deprecated")

def main():
    console = Console()
    console.print(Panel("Chọn một hành động:", style="bold green"))

    choices = [
        "Lấy bài viết Fanpage",
        "Lấy bài viết NewsFeed",
        "Đăng bài viết",
        "Đăng nhập",
        "Dọn dẹp bộ nhớ",
        "Update phiên bản",
        "Thoát"
    ]
    
    action_question = inquirer.List('action', message="Bạn muốn làm gì", choices=choices, carousel=True)
    
    answers = inquirer.prompt([action_question])

    if answers:
        action = answers['action']
        console.print(f"[bold green]Bạn đã chọn:[/] {action}")
        
        if action == "Lấy bài viết Fanpage":
            fanpage()
        elif action == "Lấy bài viết NewsFeed": 
            newsfeed()
        elif action == "Đăng bài viết": 
            post()
        elif action == "Đăng nhập": 
            login()
        elif action == "Dọn dẹp bộ nhớ": 
            periodic_cleanup()
        elif action == "Update phiên bản": 
            console = Console()
            questions = [inquirer.Confirm('confirm', message="Bạn có chắc chắn muốn cập nhật phiên bản?", default=True)]
            answers = inquirer.prompt(questions)
            if answers and answers['confirm']: 
                try:
                    subprocess.run(['git','reset','--hard'], check=True)
                    subprocess.run(['git','clean','-fd'], check=True)
                    subprocess.run(['git','pull'], check=True)
                    console.print("Cập nhật phiên bản thành công!", style="bold green")
                except subprocess.CalledProcessError as e:
                    console.print(f"Đã có lỗi khi thực thi lệnh git: {e}", style="bold red")
            else:
                console.print("Thoát chương trình.", style="bold yellow")
        else:
            console.print("Thoát chương trình.")

    else:
        console.print("Bạn đã hủy chọn.")
        
if __name__ == "__main__":
    main()
