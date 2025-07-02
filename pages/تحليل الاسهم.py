import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import time
import numpy as np
import requests
from io import StringIO

# --- إعدادات التطبيق ---
st.set_page_config(page_title="أداة الأسهم متعددة المصادر", layout="wide")
st.title('📈 أداة الأسهم الأكثر ارتفاعًا (متعددة المصادر)')

# --- إدارة مصادر البيانات ---
class DataSources:
    def __init__(self):
        self.sources = {
            "Yahoo Finance": {
                "name": "Yahoo Finance",
                "requires_key": False,
                "available": True
            },
            "Alpha Vantage": {
                "name": "Alpha Vantage",
                "requires_key": True,
                "available": False,
                "module": None
            },
            "Twelve Data": {
                "name": "Twelve Data",
                "requires_key": True,
                "available": False,
                "module": None
            },
            "Tiingo": {
                "name": "Tiingo",
                "requires_key": True,
                "available": False
            }
        }
        self._check_available_sources()

    def _check_available_sources(self):
        try:
            from alpha_vantage.timeseries import TimeSeries
            self.sources["Alpha Vantage"]["available"] = True
            self.sources["Alpha Vantage"]["module"] = TimeSeries
        except ImportError:
            pass

        try:
            import twelvedata as td
            self.sources["Twelve Data"]["available"] = True
            self.sources["Twelve Data"]["module"] = td
        except ImportError:
            pass

        self.sources["Tiingo"]["available"] = True

    def get_available_sources(self):
        return [src for src in self.sources.values() if src["available"]]

# تهيئة مصادر البيانات
data_sources = DataSources()

# --- واجهة المستخدم ---
st.sidebar.header("إعدادات المصادر")
available_sources = [src["name"] for src in data_sources.get_available_sources()]
selected_source = st.sidebar.selectbox("اختر مصدر البيانات:", available_sources, index=0)

api_keys = {}
for src in data_sources.get_available_sources():
    if src["requires_key"]:
        api_keys[src["name"]] = st.sidebar.text_input(f"مفتاح {src['name']} API:", type="password", key=f"{src['name']}_key")

# --- وظائف جلب البيانات ---
def get_yfinance_data(symbol, period="1mo"):
    try:
        data = yf.Ticker(symbol).history(period=period)
        time.sleep(0.5)
        return data[['Open', 'High', 'Low', 'Close', 'Volume']] if not data.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Yahoo Finance: {str(e)}")
        return pd.DataFrame()

def get_alphavantage_data(symbol, period="1mo"):
    if not api_keys.get("Alpha Vantage"):
        st.error("الرجاء إدخال مفتاح Alpha Vantage API")
        return pd.DataFrame()
    try:
        ts = data_sources.sources["Alpha Vantage"]["module"](key=api_keys["Alpha Vantage"], output_format='pandas')
        data, _ = ts.get_daily(symbol=symbol, outputsize='full')
        data = data.sort_index()
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return data.tail(30)
    except Exception as e:
        st.error(f"خطأ في Alpha Vantage: {str(e)}")
        return pd.DataFrame()

def get_twelvedata_data(symbol, period="1mo"):
    if not api_keys.get("Twelve Data"):
        st.error("الرجاء إدخال مفتاح Twelve Data API")
        return pd.DataFrame()
    try:
        client = data_sources.sources["Twelve Data"]["module"].Client(apikey=api_keys["Twelve Data"])
        timeframe = "1day" if "mo" in period else "1hour"
        data = client.time_series(symbol=symbol, interval=timeframe, outputsize=100, timezone="UTC").as_pandas()
        if not data.empty:
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return data.tail(30)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Twelve Data: {str(e)}")
        return pd.DataFrame()

def get_tiingo_data(symbol, period="1mo"):
    if not api_keys.get("Tiingo"):
        st.error("الرجاء إدخال مفتاح Tiingo API")
        return pd.DataFrame()
    try:
        end_date = datetime.now()
        if "mo" in period:
            months = int(period.replace("mo", ""))
            start_date = end_date - timedelta(days=months*30)
        else:
            days = int(period.replace("d", ""))
            start_date = end_date - timedelta(days=days)
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date.strftime('%Y-%m-%d')}&endDate={end_date.strftime('%Y-%m-%d')}&token={api_keys['Tiingo']}"
        headers = { 'Content-Type': 'application/json' }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = pd.read_json(StringIO(response.text))
        if not data.empty:
            data = data.set_index('date')
            data.index = pd.to_datetime(data.index)
            return data[['open', 'high', 'low', 'close', 'volume']].rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
            })
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Tiingo: {str(e)}")
        return pd.DataFrame()

# --- جاهز لتحليل البيانات لاحقًا ---
