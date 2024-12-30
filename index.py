import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from terminal.action import post,newsfeed,fanpage,login


def main():
    console = Console()
    console.print(Panel("Chọn một hành động:", style="bold green"))

    choices = [
        "Lấy bài viết Fanpage",
        "Lấy bài viết NewsFeed",
        "Đăng bài viết",
        "Đăng nhập",
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
        else:
            console.print("Thoát chương trình.")

    else:
        console.print("Bạn đã hủy chọn.")
        
if __name__ == "__main__":
    main()
