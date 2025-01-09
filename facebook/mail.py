import imaplib
import email


class MailTool:
    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd

    def connect(self, outlook=True):
        # Chọn máy chủ dựa trên email
        server = "outlook.office365.com" if outlook else "imap.gmail.com"

        try:
            # Kết nối tới máy chủ IMAP
            mailbox = imaplib.IMAP4_SSL(server)
            mailbox.login(self.user, self.pwd)
            return mailbox
        except Exception as e:
            print("IMAP login failed:", e)
            return None

    def fetch_mail(self, from_mail, limit=1):
        mailbox = self.connect(outlook="@gmail.com" not in self.user)
        if mailbox:
            try:
                mailbox.select("inbox")  # Chọn hộp thư đến
                # Tìm email từ địa chỉ cụ thể
                status, messages = mailbox.search(None, f'(FROM "{from_mail}")')
                email_ids = messages[0].split()
                result = []

                # Lấy email gần nhất (giới hạn bởi `limit`)
                for email_id in email_ids[-limit:]:
                    status, msg_data = mailbox.fetch(email_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            result.append(msg)
                return result
            except Exception as e:
                print("Error fetching email:", e)
                return []
            finally:
                mailbox.logout()
        return []




