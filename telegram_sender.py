# telegram_sender.py
import requests
import os
import streamlit as st
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

# Load environment variables
load_dotenv()

class TelegramSender:
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = self._get_telegram_token()
        self.TELEGRAM_CHAT_ID = self._get_chat_id()
        
    def _get_telegram_token(self) -> Optional[str]:
        """Get Telegram token from environment variables or Streamlit secrets"""
        token = os.getenv("TELEGRAM_BOT_TOKEN") or st.secrets.get("telegram", {}).get("bot_token")
        if not token:
            st.error("❌ Telegram token not found in environment variables or Streamlit secrets")
        return token
    
    def _get_chat_id(self) -> Optional[str]:
        """Get Telegram chat ID from environment variables or Streamlit secrets"""
        chat_id = os.getenv("TELEGRAM_CHAT_ID") or st.secrets.get("telegram", {}).get("chat_id")
        if not chat_id:
            st.error("❌ Telegram chat ID not found in environment variables or Streamlit secrets")
        return chat_id
    
    def send_message(
        self,
        message: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False,
        timeout: int = 10
    ) -> bool:
        """
        Send message to Telegram
        
        Args:
            message: Message content to send
            parse_mode: Text formatting mode (HTML or Markdown)
            disable_notification: Send silently if True
            timeout: Request timeout in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.TELEGRAM_BOT_TOKEN or not self.TELEGRAM_CHAT_ID:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": self.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            return True
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Telegram API Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                st.error(f"Response: {e.response.text}")
        except Exception as e:
            st.error(f"❌ Unexpected error sending Telegram message: {str(e)}")
            
        return False

# Helper function for backward compatibility
def send_telegram_message(message: str) -> bool:
    sender = TelegramSender()
    return sender.send_message(message)
