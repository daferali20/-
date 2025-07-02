import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from ta.volume import OnBalanceVolumeIndicator
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# تهيئة صفحة Streamlit
st.set_page_config(page_title="أداة تحليل الأسهم الصاعدة", layout="wide")
st.title('أداة تصفية الأسهم الصاعدة')

# --- قسم الإعدادات ---
st.sidebar.header("الإعدادات")

# الحصول على مفتاح API من Finnhub (يفضل تخزينه في متغيرات البيئة)
#FINNHUB_API_KEY = st.sidebar.text_input("أدخل مفتاح Finnhub API:", type="password") or os.getenv("FINNHUB_API_KEY")
FINNHUB_API_KEY = st.secrets["FINNHUB_API_KEY"]
if not FINNHUB_API_KEY:
    st.error("الرجاء إدخال مفتاح Finnhub API لاستخدام التطبيق")
    st.stop()

# --- قسم جلب البيانات ---
def get_stock_data(symbol, start_date, end_date):
    """جلب بيانات السهم من Finnhub API"""
    try:
        # جلب البيانات اليومية
        res = requests.get(
            f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={start_date}&to={end_date}&token={FINNHUB_API_KEY}"
        )
        data = res.json()
        
        if data['s'] == 'no_data':
            st.error(f"لا توجد بيانات متاحة للسهم {symbol}")
            return pd.DataFrame()
        
        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame({
            'Date': pd.to_datetime(data['t'], unit='s'),
            'Open': data['o'],
            'High': data['h'],
            'Low': data['l'],
            'Close': data['c'],
            'Volume': data['v']
        }).set_index('Date')
        
        return df
    
    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب البيانات: {str(e)}")
        return pd.DataFrame()

# --- واجهة المستخدم ---
symbol = st.text_input("أدخل رمز السهم (مثال: AAPL):", "AAPL")

# تحديد الفترة الزمنية
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
start_date_str = int(start_date.timestamp())
end_date_str = int(end_date.timestamp())

if st.button("تحليل السهم"):
    if not symbol:
        st.warning("الرجاء إدخال رمز السهم")
    else:
        with st.spinner("جلب بيانات السهم..."):
            stock_data = get_stock_data(symbol, start_date_str, end_date_str)
        
        if not stock_data.empty:
            # --- حساب المؤشرات الفنية ---
            # حساب OBV
            obv_indicator = OnBalanceVolumeIndicator(close=stock_data['Close'], volume=stock_data['Volume'])
            stock_data['OBV'] = obv_indicator.on_balance_volume()

            # حساب MFI (Money Flow Index)
            def calculate_mfi(data, window=14):
                typical_price = (data['High'] + data['Low'] + data['Close']) / 3
                money_flow = typical_price * data['Volume']
                
                positive_flow = []
                negative_flow = []
                
                for i in range(1, len(typical_price)):
                    if typical_price[i] > typical_price[i-1]:
                        positive_flow.append(money_flow[i-1])
                        negative_flow.append(0)
                    elif typical_price[i] < typical_price[i-1]:
                        negative_flow.append(money_flow[i-1])
                        positive_flow.append(0)
                    else:
                        positive_flow.append(0)
                        negative_flow.append(0)
                
                positive_mf = pd.Series(positive_flow).rolling(window).sum()
                negative_mf = pd.Series(negative_flow).rolling(window).sum()
                
                mfi = 100 - (100 / (1 + (positive_mf / negative_mf)))
                return mfi

            stock_data['MFI'] = calculate_mfi(stock_data)
            
            # حساب نسبة التغير اليومي
            stock_data['Daily_Return'] = stock_data['Close'].pct_change() * 100
            
            # حساب متوسط الحجم المتحرك (20 يوم)
            stock_data['Avg_Volume'] = stock_data['Volume'].rolling(window=20).mean()
            
            # --- تطبيق معايير التصفية ---
            filtered_stocks = stock_data[
                (stock_data['Daily_Return'] > 5) &  # ارتفاع أكثر من 5%
                (stock_data['Volume'] > stock_data['Avg_Volume']) &  # حجم أعلى من المتوسط
                (stock_data['MFI'] > 50) & (stock_data['MFI'] < 80) &  # تدفق نقدي صحي
                (stock_data['OBV'] > stock_data['OBV'].shift(1))  # OBV صاعد
            ].copy()
            
            # --- عرض النتائج ---
            st.success(f"تم تحليل بيانات السهم {symbol} بنجاح")
            
            # عرض البيانات المصفاة
            st.subheader("الأسهم المصفاة بناءً على المعايير:")
            if not filtered_stocks.empty:
                st.dataframe(filtered_stocks[['Close', 'Daily_Return', 'Volume', 'Avg_Volume', 'MFI', 'OBV']])
            else:
                st.warning("لا توجد أسهم مطابقة للمعايير في الفترة المحددة")
            
            # عرض الرسوم البيانية
            st.subheader("الرسوم البيانية")
            
            # رسم السعر مع إشارات الشراء
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(stock_data['Close'], label='السعر')
            if not filtered_stocks.empty:
                ax.scatter(filtered_stocks.index, filtered_stocks['Close'], color='green', label='إشارات شراء')
            ax.legend()
            ax.set_title(f"تحليل سعر سهم {symbol}")
            st.pyplot(fig)
            
            # رسم OBV باستخدام Plotly
            fig_obv = px.line(stock_data, x=stock_data.index, y='OBV', title=f"مؤشر OBV لسهم {symbol}")
            st.plotly_chart(fig_obv)
            
            # رسم MFI باستخدام Plotly
            fig_mfi = px.line(stock_data, x=stock_data.index, y='MFI', title=f"مؤشر MFI لسهم {symbol}")
            fig_mfi.add_hline(y=50, line_dash="dash", line_color="gray")
            fig_mfi.add_hline(y=80, line_dash="dash", line_color="red")
            st.plotly_chart(fig_mfi)
            
        else:
            st.error("فشل في جلب بيانات السهم. الرجاء التحقق من رمز السهم والمفتاح API")
