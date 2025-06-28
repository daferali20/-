# config.py
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.alpha_key = (
            os.getenv("ALPHA_VANTAGE_API_KEY") or
            st.secrets.get("alpha_vantage", {}).get("api_key", "")
        )

config = Config()
