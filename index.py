import inquirer
from rich.console import Console
from rich.panel import Panel
import subprocess
from rich.text import Text
import warnings
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
        elif action == "Update phiên bản": 
            try:
                subprocess.run(['git','reset','--hard'],check=True)
                subprocess.run(['git','clean','-fd'],check=True)
                subprocess.run(['git','pull'],check=True)
                print("Cập nhật phiên bản thành công!")
            except subprocess.CalledProcessError as e:
                print(f"Đã có lỗi khi thực thi lệnh git: {e}")
        else:
            console.print("Thoát chương trình.")

    else:
        console.print("Bạn đã hủy chọn.")
        
if __name__ == "__main__":
    main()
