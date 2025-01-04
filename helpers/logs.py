import os
from datetime import datetime

def log(account, message, filename='log.txt'):
    log_directory = 'logs'
    log_file = filename
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Kiểm tra nếu account là None, và nếu có, đặt tên mặc định
    if account is None:
        account_name = 'Unknown'
    else:
        account_name = account.get('name', 'Unknown')  # Sử dụng 'Unknown' nếu không có 'name'
    
    message = f"{timestamp} - {account_name} - {message}"
    
    # Ensure the log directory exists
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    # Write the message to the log file with utf-8 encoding to handle special characters
    with open(os.path.join(log_directory, log_file), 'a', encoding='utf-8') as file:
        file.write(message + '\n')

def log_push(account, message):
    log(account, message, 'push.txt')

def log_newsfeed(account, message):
    log(account, message, 'newsfeed.txt')
