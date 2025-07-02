import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import time
import numpy as np

# استيراد Twelve Data مع معالجة الخطأ
try:
    import twelvedata as td
    TWELVE_DATA_AVAILABLE = True
except ImportError:
    TWELVE_DATA_AVAILABLE = False
    st.warning("ملاحظة: مكتبة TwelveData غير مثبتة. سيتم تعطيل خيار TwelveData.")

# استيراد Alpha Vantage مع معالجة الخطأ
try:
    from alpha_vantage.timeseries import TimeSeries
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    st.warning("ملاحظة: مكتبة AlphaVantage غير مثبتة. سيتم تعطيل خيار AlphaVantage.")

# إعداد واجهة المستخدم
st.set_page_config(page_title="أداة الأسهم متعددة المصادر", layout="wide")
st.title('📈 أداة الأسهم الأكثر ارتفاعًا')

# قائمة مصادر البيانات المتاحة
available_sources = ["Yahoo Finance"]

if ALPHA_VANTAGE_AVAILABLE:
    available_sources.append("Alpha Vantage")
if TWELVE_DATA_AVAILABLE:
    available_sources.append("Twelve Data")

# اختيار مصدر البيانات
data_source = st.sidebar.selectbox(
    "اختر مصدر البيانات:",
    available_sources,
    index=0
)

# إدارة مفاتيح API
if data_source == "Alpha Vantage" and ALPHA_VANTAGE_AVAILABLE:
    av_key = st.sidebar.text_input("أدخل مفتاح Alpha Vantage API:", type="password")
elif data_source == "Twelve Data" and TWELVE_DATA_AVAILABLE:
    td_key = st.sidebar.text_input("أدخل مفتاح Twelve Data API:", type="password")

# --- وظائف جلب البيانات ---
def get_stock_data(symbol, period="1mo"):
    """دالة موحدة لجلب البيانات من المصدر المحدد"""
    try:
        if data_source == "Yahoo Finance":
            return get_yfinance_data(symbol, period)
        elif data_source == "Alpha Vantage":
            return get_alphavantage_data(symbol, period) if ALPHA_VANTAGE_AVAILABLE else pd.DataFrame()
        elif data_source == "Twelve Data":
            return get_twelvedata_data(symbol, period) if TWELVE_DATA_AVAILABLE else pd.DataFrame()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return pd.DataFrame()

def get_twelvedata_data(symbol, period):
    """جلب البيانات من Twelve Data"""
    if not TWELVE_DATA_AVAILABLE or not td_key:
        st.error("Twelve Data غير متاح. الرجاء تثبيت المكتبة وإدخال المفتاح")
        return pd.DataFrame()
    
    try:
        client = td.Client(apikey=td_key)
        timeframe = "1day" if "mo" in period else "1hour"
        
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

# باقي الكود (وظائف get_yfinance_data و get_alphavantage_data وواجهة المستخدم) ...
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
