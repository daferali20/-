# telegram_sender.py

import requests
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env (اختياري إذا كنت تستخدم Streamlit Cloud secrets)
load_dotenv()

# يمكنك استخدام هذه القيم من secrets.toml أيضًا
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or st.secrets["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or st.secrets["telegram"]["chat_id"]

def send_telegram_message(message: str) -> bool:
    """
    إرسال رسالة إلى تليجرام باستخدام البوت.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"خطأ أثناء إرسال رسالة Telegram: {str(e)}")
        return False
