import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import time
import numpy as np
from alpha_vantage.timeseries import TimeSeries
import twelvedata as td
import cachetools

# تهيئة التطبيق
st.set_page_config(page_title="أداة الأسهم متعددة المصادر", layout="wide")
st.title('📈 أداة الأسهم الأكثر ارتفاعًا (متعددة المصادر)')

# إعدادات التطبيق
st.sidebar.header("إعدادات المصادر")
data_source = st.sidebar.selectbox(
    "اختر مصدر البيانات:",
    ["Yahoo Finance", "Alpha Vantage", "Twelve Data"],
    index=0
)

# إعداد مفاتيح API
if data_source == "Alpha Vantage":
    av_key = st.sidebar.text_input("أدخل مفتاح Alpha Vantage API:", type="password")
elif data_source == "Twelve Data":
    td_key = st.sidebar.text_input("أدخل مفتاح Twelve Data API:", type="password")

MAX_RETRIES = 3
DELAY = 2
cache = cachetools.TTLCache(maxsize=100, ttl=3600)

# --- وظائف جلب البيانات من مصادر مختلفة ---
@cachetools.cached(cache)
def get_stock_data(symbol, period="1mo"):
    """دالة موحدة لجلب البيانات من المصدر المحدد"""
    try:
        if data_source == "Yahoo Finance":
            return get_yfinance_data(symbol, period)
        elif data_source == "Alpha Vantage" and av_key:
            return get_alphavantage_data(symbol, period)
        elif data_source == "Twelve Data" and td_key:
            return get_twelvedata_data(symbol, period)
        else:
            st.error("المفتاح المطلوب غير متوفر لهذا المصدر")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return pd.DataFrame()

def get_yfinance_data(symbol, period):
    """جلب البيانات من Yahoo Finance"""
    for _ in range(MAX_RETRIES):
        try:
            data = yf.Ticker(symbol).history(period=period)
            time.sleep(DELAY)
            if not data.empty:
                return data[['Open', 'High', 'Low', 'Close', 'Volume']]
        except:
            time.sleep(DELAY * 2)
    return pd.DataFrame()

def get_alphavantage_data(symbol, period):
    """جلب البيانات من Alpha Vantage"""
    try:
        ts = TimeSeries(key=av_key, output_format='pandas')
        
        # تحديد الفترة بناءً على المدخلات
        if "mo" in period:
            interval = 'daily'
            outputsize = 'compact'
        else:
            interval = '60min'
            outputsize = 'compact'
        
        data, _ = ts.get_daily(symbol=symbol, outputsize='full')
        data = data.sort_index()
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return data.last(period)
    except Exception as e:
        st.error(f"خطأ في Alpha Vantage: {str(e)}")
        return pd.DataFrame()

def get_twelvedata_data(symbol, period):
    """جلب البيانات من Twelve Data"""
    try:
        client = td.Client(apikey=td_key)
        
        # تحويل الفترة إلى صيغة Twelve Data
        if "mo" in period:
            months = int(period.replace("mo", ""))
            timeframe = "1day"
        else:
            timeframe = "1hour"
        
        data = client.time_series(
            symbol=symbol,
            interval=timeframe,
            outputsize=100,
            timezone="UTC"
        ).as_pandas()
        
        if not data.empty:
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return data.last(period)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Twelve Data: {str(e)}")
        return pd.DataFrame()

# --- واجهة التطبيق ---
tab1, tab2 = st.tabs(["الأسهم الصاعدة", "تحليل مفصل"])

with tab1:
    st.header("الأسهم الأكثر ارتفاعًا")
    
    market = st.selectbox("اختر السوق:", ["NASDAQ", "Tadawul"])
    
    if st.button("جلب البيانات"):
        with st.spinner("جاري التحليل..."):
            if market == "NASDAQ":
                symbols = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA"]
            else:
                symbols = ["2222.SR", "1180.SR", "7010.SR", "1211.SR", "2380.SR"]
            
            results = []
            for symbol in symbols:
                data = get_stock_data(symbol)
                if not data.empty and len(data) > 1:
                    change_pct = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                    results.append({
                        'السهم': symbol,
                        'السعر': data['Close'].iloc[-1],
                        'التغير %': change_pct,
                        'الحجم': data['Volume'].iloc[-1],
                        'المصدر': data_source
                    })
                time.sleep(DELAY)
            
            if results:
                df = pd.DataFrame(results).sort_values('التغير %', ascending=False)
                st.dataframe(
                    df.style
                    .highlight_max(subset=['التغير %'], color='lightgreen')
                    .format({'السعر': "{:.2f}", 'التغير %': "{:.2f}%", 'الحجم': "{:,.0f}"}),
                    hide_index=True
                )
            else:
                st.warning("لا توجد بيانات متاحة. حاول تغيير مصدر البيانات.")

with tab2:
    st.header("تحليل مفصل للسهم")
    symbol = st.text_input("ادخل رمز السهم:", "AAPL")
    
    if st.button("تحليل السهم"):
        if not symbol:
            st.warning("الرجاء إدخال رمز السهم")
        else:
            with st.spinner("جاري التحليل..."):
                data = get_stock_data(symbol, "3mo")
                
                if not data.empty:
                    # تحليل البيانات
                    data['Daily_Return'] = data['Close'].pct_change() * 100
                    data['SMA_20'] = data['Close'].rolling(20).mean()
                    
                    # عرض النتائج
                    col1, col2 = st.columns(2)
                    col1.metric("آخر سعر", f"{data['Close'].iloc[-1]:.2f}")
                    col1.metric("التغير اليومي", f"{data['Daily_Return'].iloc[-1]:.2f}%")
                    col2.metric("حجم التداول", f"{data['Volume'].iloc[-1]:,.0f}")
                    col2.metric("المتوسط المتحرك", f"{data['SMA_20'].iloc[-1]:.2f}")
                    
                    # الرسوم البيانية
                    fig1 = px.line(data, x=data.index, y=['Close', 'SMA_20'], 
                                 title=f"أداء السهم {symbol} (مصدر: {data_source})")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    fig2 = px.bar(data, x=data.index, y='Volume',
                                 title=f"حجم التداول لـ {symbol}")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.error("فشل في جلب البيانات. حاول:")
                    st.markdown("""
                    1. تغيير مصدر البيانات
                    2. التحقق من صحة الرمز
                    3. التأكد من صحة مفتاح API
                    """)

# نصائح الاستخدام
st.sidebar.markdown("""
**نصائح مهمة:**
1. Yahoo Finance لا يحتاج لمفتاح API
2. Alpha Vantage وTwelve Data يحتاجان مفاتيح API
3. استخدم رمز السوق الصحيح (مثل .SR للأسهم السعودية)
4. عند حدوث أخطاء، جرب مصدر بيانات مختلف
""")
