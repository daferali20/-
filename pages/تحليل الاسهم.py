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

st.sidebar.subheader("فلترة الأسهم")
min_price = st.sidebar.number_input("السعر الأدنى", min_value=0.0, value=1.0)
max_price = st.sidebar.number_input("السعر الأعلى", min_value=1.0, value=55.0)
limit_results = st.sidebar.number_input("عدد الأسهم الظاهرة", min_value=1, max_value=100, value=10)

# --- إعداد مصدر بيانات خارجي ---
@st.cache_data(ttl=300)
def get_most_active_stocks():
    try:
        url = f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={st.secrets['FMP_API_KEY']}"
        response = requests.get(url)
        stocks = pd.DataFrame(response.json())
        return stocks
    except Exception as e:
        st.error(f"خطأ في جلب قائمة الأسهم: {str(e)}")
        return pd.DataFrame()

# --- تبويب الأسهم الصاعدة ---
st.header("📊 الأسهم الأكثر ارتفاعًا")
if st.button("🔍 تحليل الأسهم"):
    with st.spinner("جاري تحليل السوق..."):
        stocks = get_most_active_stocks()
        if not stocks.empty:
            stocks = stocks[(stocks['price'] >= min_price) & (stocks['price'] <= max_price)]
            stocks['التغير %'] = stocks['changesPercentage'].str.replace('%', '').astype(float)
            stocks = stocks.sort_values('التغير %', ascending=False).head(limit_results)

            df = stocks[['symbol', 'name', 'price', 'التغير %', 'volume']].rename(columns={
                'symbol': 'الرمز', 'name': 'اسم الشركة', 'price': 'السعر', 'volume': 'الحجم'
            })

            st.dataframe(
                df.style.format({'السعر': '{:.2f}', 'التغير %': '{:.2f}%', 'الحجم': '{:,.0f}'}),
                use_container_width=True
            )
        else:
            st.warning("لم يتم العثور على بيانات متاحة.")

# --- تحليل مفصل لسهم محدد ---
st.subheader("📌 تحليل مفصل لسهم معين")
symbol = st.text_input("أدخل رمز السهم (مثال: AAPL):", "AAPL")
if st.button("تحليل السهم"):
    with st.spinner("جاري تحليل السهم..."):
        try:
            data = yf.Ticker(symbol).history(period="3mo")
            data['Daily_Return'] = data['Close'].pct_change() * 100
            data['SMA_20'] = data['Close'].rolling(20).mean()
            last_row = data.iloc[-1]

            col1, col2 = st.columns(2)
            col1.metric("آخر سعر", f"{last_row['Close']:.2f}")
            col1.metric("التغير اليومي", f"{last_row['Daily_Return']:.2f}%")
            col2.metric("الحجم", f"{last_row['Volume']:,.0f}")
            col2.metric("SMA 20", f"{last_row['SMA_20']:.2f}")

            fig1 = px.line(data, x=data.index, y=['Close', 'SMA_20'],
                           title=f"أداء السهم {symbol}")
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.bar(data, x=data.index, y='Volume', title="حجم التداول")
            st.plotly_chart(fig2, use_container_width=True)

        except Exception as e:
            st.error(f"حدث خطأ أثناء تحليل السهم: {str(e)}")

st.markdown("""
---
**ملاحظات مهمة:**
- الأسعار قد تكون متأخرة قليلاً حسب المصدر.
- يجب إدخال مفتاح API صالح في إعدادات `secrets.toml`:
```toml
[FMP_API_KEY]
value = "YOUR_API_KEY"
```
""")
