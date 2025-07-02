import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# تهيئة صفحة Streamlit
st.set_page_config(page_title="أداة تحليل الأسهم الصاعدة", layout="wide")
st.title('📈 أداة تحليل الأسهم الأكثر ارتفاعًا')

# --- قسم الإعدادات ---
st.sidebar.header("الإعدادات")

# تحميل مفتاح API من أسرار Streamlit
try:
    FINNHUB_API_KEY = st.secrets["FINNHUB_API_KEY"]
except:
    st.error("الرجاء إعداد مفتاح Finnhub API في ملف secrets.toml")
    st.stop()

# --- وظائف تحليل البيانات ---
def get_top_gainers():
    """جلب قائمة الأسهم الأكثر ارتفاعًا من Finnhub"""
    try:
        url = f"https://finnhub.io/api/v1/stock/gainers?token={FINNHUB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return pd.DataFrame()

def get_stock_data(symbol, days=30):
    """جلب بيانات تاريخية للسهم"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_unix = int(start_date.timestamp())
        end_unix = int(end_date.timestamp())
        
        url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution=D&from={start_unix}&to={end_unix}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data['s'] == 'no_data':
            return pd.DataFrame()
        
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
        st.error(f"خطأ في جلب بيانات السهم: {str(e)}")
        return pd.DataFrame()

def calculate_obv(df):
    """حساب مؤشر OBV يدويًا"""
    obv = [0]
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return obv

def calculate_mfi(df, window=14):
    """حساب مؤشر MFI يدويًا"""
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    mf = tp * df['Volume']
    
    pos_mf = []
    neg_mf = []
    
    for i in range(1, len(tp)):
        if tp.iloc[i] > tp.iloc[i-1]:
            pos_mf.append(mf.iloc[i-1])
            neg_mf.append(0)
        elif tp.iloc[i] < tp.iloc[i-1]:
            neg_mf.append(mf.iloc[i-1])
            pos_mf.append(0)
        else:
            pos_mf.append(0)
            neg_mf.append(0)
    
    pos_mf = pd.Series(pos_mf).rolling(window).sum()
    neg_mf = pd.Series(neg_mf).rolling(window).sum()
    
    mfi = 100 - (100 / (1 + (pos_mf / neg_mf)))
    return mfi

# --- واجهة التطبيق الرئيسية ---
tab1, tab2 = st.tabs(["الأسهم الأكثر ارتفاعًا", "تحليل سهم معين"])

with tab1:
    st.header("قائمة الأسهم الأكثر ارتفاعًا")
    
    if st.button("جلب أحدث البيانات"):
        with st.spinner("جاري تحليل الأسهم..."):
            gainers_df = get_top_gainers()
            
            if not gainers_df.empty:
                # تحليل كل سهم في القائمة
                results = []
                for symbol in gainers_df['symbol'].head(20):  # تحليل أول 20 سهم فقط للأداء
                    stock_data = get_stock_data(symbol)
                    if not stock_data.empty:
                        # حساب المؤشرات
                        stock_data['OBV'] = calculate_obv(stock_data)
                        stock_data['MFI'] = calculate_mfi(stock_data)
                        stock_data['Daily_Return'] = stock_data['Close'].pct_change() * 100
                        stock_data['Avg_Volume'] = stock_data['Volume'].rolling(20).mean()
                        
                        # تقييم السهم
                        last_day = stock_data.iloc[-1]
                        prev_day = stock_data.iloc[-2]
                        
                        # المعايير
                        is_rising = last_day['Close'] > prev_day['Close']
                        high_volume = last_day['Volume'] > last_day['Avg_Volume']
                        obv_rising = last_day['OBV'] > prev_day['OBV']
                        mfi_ok = 50 < last_day['MFI'] < 80
                        
                        # تقييم القوة
                        if is_rising and high_volume and obv_rising and mfi_ok:
                            strength = "قوي"
                        elif is_rising and high_volume and not obv_rising:
                            strength = "تحذير: OBV متناقض"
                        else:
                            strength = "ضعيف"
                        
                        results.append({
                            'السهم': symbol,
                            'السعر الأخير': last_day['Close'],
                            'التغير %': last_day['Daily_Return'],
                            'الحجم': last_day['Volume'],
                            'متوسط الحجم': last_day['Avg_Volume'],
                            'OBV': "صاعد" if obv_rising else "هابط",
                            'MFI': round(last_day['MFI'], 2),
                            'القوة': strength
                        })
                
                # عرض النتائج
                results_df = pd.DataFrame(results)
                st.dataframe(results_df.sort_values('القوة', ascending=False))
                
                # عرض أفضل الأسهم
                st.subheader("أفضل الأسهم ذات المؤشرات القوية")
                strong_stocks = results_df[results_df['القوة'] == "قوي"]
                if not strong_stocks.empty:
                    for _, stock in strong_stocks.iterrows():
                        st.success(f"✅ {stock['السهم']}: سعر {stock['السعر الأخير']} (تغير {stock['التغير %']:.2f}%) - حجم تداول {stock['الحجم']:,.0f}")
                else:
                    st.warning("لا توجد أسهم ذات مؤشرات قوية اليوم")
            else:
                st.error("لا يمكن جلب بيانات الأسهم الأكثر ارتفاعًا")

with tab2:
    st.header("تحليل سهم معين")
    symbol = st.text_input("أدخل رمز السهم (مثال: AAPL):", "AAPL")
    
    if st.button("تحليل السهم"):
        if not symbol:
            st.warning("الرجاء إدخال رمز السهم")
        else:
            with st.spinner(f"جاري تحليل سهم {symbol}..."):
                stock_data = get_stock_data(symbol)
                
                if not stock_data.empty:
                    # حساب المؤشرات
                    stock_data['OBV'] = calculate_obv(stock_data)
                    stock_data['MFI'] = calculate_mfi(stock_data)
                    stock_data['Daily_Return'] = stock_data['Close'].pct_change() * 100
                    stock_data['Avg_Volume'] = stock_data['Volume'].rolling(20).mean()
                    
                    # تحليل آخر يوم
                    last_day = stock_data.iloc[-1]
                    prev_day = stock_data.iloc[-2]
                    
                    # عرض النتائج
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("السعر الأخير", f"{last_day['Close']:.2f}")
                        st.metric("التغير اليومي", f"{last_day['Daily_Return']:.2f}%")
                        
                    with col2:
                        st.metric("حجم التداول", f"{last_day['Volume']:,.0f}", 
                                 f"{'▲ فوق المتوسط' if last_day['Volume'] > last_day['Avg_Volume'] else '▼ تحت المتوسط'}")
                        st.metric("مؤشر OBV", "صاعد ▲" if last_day['OBV'] > prev_day['OBV'] else "هابط ▼")
                    
                    # تحليل القوة
                    st.subheader("تقييم قوة السهم")
                    if last_day['Close'] > prev_day['Close']:
                        if last_day['Volume'] > last_day['Avg_Volume']:
                            if last_day['OBV'] > prev_day['OBV']:
                                st.success("✅ إشارة قوية: السهم صاعد بحجم تداول مرتفع وتأكيد من OBV")
                            else:
                                st.warning("⚠️ تحذير: السهم صاعد ولكن OBV هابط - ضعف محتمل في الاتجاه")
                        else:
                            st.warning("⚠️ تحذير: السهم صاعد ولكن بحجم تداول منخفض")
                    else:
                        st.error("❌ السهم ليس في اتجاه صاعد اليوم")
                    
                    # الرسوم البيانية
                    st.subheader("الرسوم البيانية")
                    
                    fig1 = px.line(stock_data, x=stock_data.index, y='Close', 
                                 title=f"تحليل سعر سهم {symbol}")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    fig2 = px.line(stock_data, x=stock_data.index, y='OBV', 
                                 title=f"مؤشر OBV لسهم {symbol}")
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    fig3 = px.line(stock_data, x=stock_data.index, y='MFI', 
                                 title=f"مؤشر MFI لسهم {symbol}")
                    fig3.add_hline(y=50, line_dash="dash", line_color="gray")
                    fig3.add_hline(y=80, line_dash="dash", line_color="red")
                    st.plotly_chart(fig3, use_container_width=True)
                    
                else:
                    st.error("فشل في جلب بيانات السهم. الرجاء التحقق من رمز السهم")
