import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import time
import numpy as np

# تهيئة التطبيق
st.set_page_config(page_title="أداة الأسهم الصاعدة - معدل", layout="wide")
st.title('📈 أداة الأسهم الأكثر ارتفاعًا (معدلة)')

# إعدادات التطبيق
st.sidebar.header("إعدادات التطبيق")
MAX_RETRIES = 3  # عدد المحاولات عند الفشل
DELAY = 2  # تأخير بين الطلبات (بالثواني)

# --- وظائف محسنة مع معالجة الأخطاء ---
def safe_yfinance_request(symbol, period="1mo", retries=MAX_RETRIES):
    """دالة محسنة لجلب البيانات مع إدارة معدل الطلبات"""
    for attempt in range(retries):
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            time.sleep(DELAY)  # تأخير بين الطلبات
            return hist[['Open', 'High', 'Low', 'Close', 'Volume']] if not hist.empty else pd.DataFrame()
        except Exception as e:
            if attempt == retries - 1:
                st.error(f"فشل جلب بيانات {symbol} بعد {retries} محاولات. الخطأ: {str(e)}")
            time.sleep(DELAY * 2)  # زيادة التأخير مع كل محاولة فاشلة
    return pd.DataFrame()

def get_top_gainers_safe(market="NASDAQ", max_stocks=10):
    """دالة محسنة لجلب الأسهم الصاعدة مع التحكم في المعدل"""
    try:
        if market == "Tadawul":
            tickers = ["2222.SR", "1180.SR", "7010.SR", "1211.SR", "2380.SR"]
        else:
            tickers = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA", "PYPL", "ADBE", "NFLX"]
        
        results = []
        for symbol in tickers[:max_stocks]:
            data = safe_yfinance_request(symbol)
            if not data.empty:
                results.append({
                    'Symbol': symbol,
                    'Last Close': data['Close'].iloc[-1],
                    '% Change': ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100,
                    'Volume': data['Volume'].iloc[-1]
                })
            time.sleep(DELAY)
        
        return pd.DataFrame(results).sort_values('% Change', ascending=False)
    except Exception as e:
        st.error(f"خطأ في جلب القائمة: {str(e)}")
        return pd.DataFrame()

# --- واجهة التطبيق المحسنة ---
tab1, tab2 = st.tabs(["الأسهم الصاعدة", "تحليل مفصل"])

with tab1:
    st.header("الأسهم الأكثر ارتفاعًا")
    market = st.selectbox("اختر السوق:", ["NASDAQ", "Tadawul"])
    
    if st.button("جلب البيانات", key="fetch_btn"):
        with st.spinner("جاري التحليل مع مراعاة حدود الخدمة..."):
            gainers = get_top_gainers_safe(market)
            
            if not gainers.empty:
                # تحسين عرض البيانات
                gainers['% Change'] = gainers['% Change'].apply(lambda x: f"{x:.2f}%")
                gainers['Volume'] = gainers['Volume'].apply(lambda x: f"{x:,.0f}")
                
                st.dataframe(
                    gainers.style
                    .highlight_max(subset=['% Change'], color='lightgreen')
                    .format({'Last Close': "{:.2f}"}),
                    hide_index=True,
                    use_container_width=True
                )
                
                # عرض أفضل سهم
                best = gainers.iloc[0]
                st.success(f"أفضل أداء: {best['Symbol']} بتغير {best['% Change']}")
            else:
                st.warning("لا توجد بيانات متاحة حالياً. يرجى المحاولة لاحقاً.")

with tab2:
    st.header("تحليل مفصل للسهم")
    symbol = st.text_input("ادخل رمز السهم:", "AAPL", key="symbol_input")
    
    if st.button("تحليل السهم", key="analyze_btn"):
        if not symbol:
            st.warning("الرجاء إدخال رمز السهم")
        else:
            with st.spinner("جاري التحليل بسرعات آمنة..."):
                data = safe_yfinance_request(symbol, period="3mo")
                
                if not data.empty:
                    # حساب المؤشرات
                    data['Daily Return'] = data['Close'].pct_change() * 100
                    data['SMA_20'] = data['Close'].rolling(20).mean()
                    
                    # العرض
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("آخر سعر", f"{data['Close'].iloc[-1]:.2f}")
                        st.metric("التغير اليومي", f"{data['Daily Return'].iloc[-1]:.2f}%")
                    
                    with col2:
                        st.metric("حجم التداول", f"{data['Volume'].iloc[-1]:,.0f}")
                        st.metric("المتوسط المتحرك (20 يوم)", f"{data['SMA_20'].iloc[-1]:.2f}")
                    
                    # الرسوم البيانية
                    fig1 = px.line(data, x=data.index, y=['Close', 'SMA_20'], 
                                 title=f"أداء السهم {symbol}")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    fig2 = px.bar(data, x=data.index, y='Volume',
                                title=f"حجم التداول لـ {symbol}")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.error("فشل في جلب بيانات السهم. تأكد من الرمز وحاول لاحقاً.")

# نصائح للمستخدم
st.sidebar.markdown("""
**نصائح الاستخدام:**
1. لا تضغط على الأزرار بشكل متكرر
2. استخدم تأخير 2-3 ثواني بين الطلبات
3. للأسهم السعودية استخدم صيغة 2222.SR
4. جرب أوقات غير الذروة
""")
