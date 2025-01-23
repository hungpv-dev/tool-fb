import asyncio
from telegram import Bot
import requests
import logging

class BotTelegram:
    def __init__(self, token):
        self.token = token
        self.bot = Bot(token)
    
    def createChat(self):
        url = f'https://api.telegram.org/bot{self.token}/getUpdates'
        response = requests.get(url)
        data = response.json()
        
        # Xử lý nếu response không trả về 'result'
        if 'result' not in data:
            logging.error("Không tìm thấy trường 'result' trong API response.")
            self.chat_ids = []
            return self

        chat_ids = set()
        for chat in data['result']:
            if 'message' in chat and 'chat' in chat['message']:
                chat_id = chat['message']['chat']['id']
                chat_ids.add(chat_id)
        self.chat_ids = list(chat_ids)
        return self
    
    async def send_messages(self, message=''):
        await self.bot.send_message(chat_id='-4746381732', text=message)
        logging.info(f"Đã gửi tin nhắn tới chat_id: {4746381732}")
        return
        for chat_id in self.chat_ids:
            try:
                await self.bot.send_message(chat_id=chat_id, text=message)
                logging.info(f"Đã gửi tin nhắn tới chat_id: {chat_id}")
            except Exception as e:
                logging.error(f"Lỗi khi gửi tin nhắn tới chat_id {chat_id}: {e}")


# Tạo hàm send_message để sử dụng ở nơi khác
async def send_message(message):
    try:
        TOKEN = '7914192265:AAFdqhdCCRTOBWoszckui-fDrMhMu0iXWzA'
        bot_instance = BotTelegram(TOKEN)
        bot = bot_instance.createChat()
        await bot.send_messages(message)
    except Exception as e:
        print(e)
        logging.error(e)

def send(message):
    asyncio.run(send_message(message))

