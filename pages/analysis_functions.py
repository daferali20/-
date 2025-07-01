import yfinance as yf
import pandas as pd
import numpy as np
import requests
import cv2
from io import BytesIO
from PIL import Image, ImageDraw
from datetime import datetime, timedelta
# from tensorflow.keras.models import load_model  ← تم التعليق عليه
# from tensorflow.keras.preprocessing import image as kimage  ← تم التعليق عليه

# ↓↓↓ وظائف بديلة (أو مؤقتة) بدل نموذج التعلم العميق ↓↓↓

#-def fetch_tradingview_chart(ticker, interval='1D', study_params=None):
    #"""
   # جلب شارت TradingView لأي سهم
    #"""
    #base_url = "https://www.tradingview.com/chart/"
    #params = {
    #    'symbol': ticker,
    #    'interval': interval,
    #    'studies': study_params or 'MA5,MA20,RSI14'
   # }
   # try:
    #    response = requests.get(base_url, params=params, stream=True)
    #    response.raise_for_status()
    #    img = Image.open(BytesIO(response.content))
    #    return img
    #except Exception as e:
     #   raise Exception(f"خطأ في جلب الشارت: {e}")
#---------------------------------------------------------------
#from PIL import Image, ImageDraw

def fetch_tradingview_chart(ticker, timeframe="1D"):
    # إنشاء صورة وهمية (Placeholder)
    img = Image.new("RGB", (800, 400), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), f"Chart for {ticker} ({timeframe})", fill="black")
    return img

def preprocess_chart_image(img: Image.Image) -> np.ndarray:
    """
    تحويل الصورة إلى صيغة جاهزة للتحليل (رمادية ومصفوفة NumPy)
    """
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    img_resized = cv2.resize(img_cv, (224, 224))
    return img_resized

def detect_chart_patterns(image_array: np.ndarray) -> str:
    """
    محاكاة اكتشاف نمط فني دون استخدام نموذج تعلم عميق
    """
    # يمكنك لاحقًا استبداله بتحليل حقيقي
    return "مقاومة مكسورة" if np.mean(image_array) > 100 else "نمط غير واضح"

def analyze_technical_indicators(df: pd.DataFrame) -> dict:
    """
    تحليل المؤشرات الفنية مثل RSI وSMA
    """
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["RSI"] = compute_rsi(df["Close"])
    return {
        "SMA_20": df["SMA_20"].iloc[-1],
        "RSI": df["RSI"].iloc[-1]
    }

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    حساب مؤشر القوة النسبية RSI
    """
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_trading_recommendation(pattern: str, indicators: dict) -> str:
    """
    توليد توصية تداول بناءً على النمط والمؤشرات الفنية
    """
    rsi = indicators.get("RSI", 50)
    if pattern == "مقاومة مكسورة" and rsi < 70:
        return "✅ توصية شراء"
    elif rsi > 70:
        return "⚠️ تشبع شرائي، انتبه"
    else:
        return "❌ لا توجد توصية واضحة"
