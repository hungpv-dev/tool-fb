from imap_tools import MailBox, AND

# Thông tin tài khoản Outlook
email = 'kartyati697181@hotmail.com'
password = 'ohJKbfX558'

# Kết nối đến máy chủ IMAP của Outlook
with MailBox('outlook.office365.com').login(email, password, 'INBOX') as mailbox:
    # Lấy danh sách email
    for msg in mailbox.fetch(AND(seen=False)):  # fetch các email chưa đọc
        print(f"From: {msg.from_}")
        print(f"Subject: {msg.subject}")
        print(f"Date: {msg.date}")
        print(f"Body: {msg.text}")
