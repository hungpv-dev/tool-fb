from facebook.mail import MailTool

# Sử dụng lớp MailTool để kết nối và lấy email
mail = MailTool(outlook=True)

# Lấy các email từ "facebook.com", chỉ lấy 1 email đầu tiên
messages = mail.get_mail("facebook.com", limit=1)

# Chỉ in thông tin của email đầu tiên
for msg in messages:
    print("From:", msg.from_)
    print("Subject:", msg.subject)
    print("Date:", msg.date)
    
    # In ra nội dung văn bản (text body)
    print("Text body:", msg.text)  # Nội dung email dưới dạng văn bản
    
    # In ra nội dung HTML (nếu có)
    if msg.html:
        print("HTML body:", msg.html)  # Nội dung email dưới dạng HTML (nếu có)
    
    print("-" * 50)
