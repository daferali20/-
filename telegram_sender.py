# telegram_sender.py
import requests
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or st.secrets["telegram"]["bot_token"]
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or st.secrets["telegram"]["chat_id"]

def send_telegram_message(message: str) -> bool:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            st.error(f"❌ فشل الإرسال - Status Code: {response.status_code}")
            st.text(response.text)
            return False
        return True
    except Exception as e:
        st.error(f"❌ استثناء أثناء الإرسال: {str(e)}")
        return False
