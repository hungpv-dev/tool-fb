from imap_tools import MailBox, A

class MailTool:
    def __init__(self, outlook=True):
        if outlook:
            # Outlook
            self.user = "leneavepjz407413@hotmail.com"
            self.pwd = "kkfsxxavznqhrqnm"  # Mật khẩu ứng dụng
            self.server = "outlook.office365.com"
        else:
            # Gmail
            self.user = "azhung08102004@gmail.com"
            self.pwd = "kylsioybcnxgflex"  # Mật khẩu ứng dụng
            self.server = "imap.gmail.com"

    def connect(self):
        try:
            # Kết nối đến MailBox qua imap_tools
            with MailBox(self.server).login(self.user, self.pwd) as mailbox:
                return mailbox
        except Exception as e:
            print("IMAP login failed:", e)
            return None

    def get_mail(self, fromMail, limit=1):
        with self.connect() as mailbox:
            if mailbox:
                messages = mailbox.fetch(A(from_=fromMail), limit=limit)
                return messages
            else:
                print("Không thể kết nối đến mailbox.")
                return []