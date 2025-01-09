from facebook.mail import MailTool

 # Gmail
# user = "azhung08102004@gmail.com"
# pwd = "kylsioybcnxgflex"  # Mật khẩu ứng dụng

# Outlook
user = "leneavepjz407413@hotmail.com"
pwd = "kkfsxxavznqhrqnm"  # Mật khẩu ứng dụng

mail = MailTool(user, pwd)
emails = mail.fetch_mail("facebook", limit=1)  # Tìm email từ Facebook

for msg in emails:
    print(f"Subject: {msg['subject']}")
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                print(f"Body: {part.get_payload(decode=True).decode()}")
    else:
        print(f"Body: {msg.get_payload(decode=True).decode()}")