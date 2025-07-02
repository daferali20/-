import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# تهيئة صفحة Streamlit
st.set_page_config(page_title="أداة تحليل الأسهم الصاعدة - Yahoo Finance", layout="wide")
st.title('📈 أداة تحليل الأسهم الأكثر ارتفاعًا (Yahoo Finance)')

# --- وظائف تحليل البيانات ---
def get_top_gainers_market(market):
    """جلب الأسهم الأكثر ارتفاعًا من Yahoo Finance حسب السوق"""
    try:
        if market == "NASDAQ":
            url = "https://finance.yahoo.com/gainers?offset=0&count=100"
        elif market == "NYSE":
            url = "https://finance.yahoo.com/gainers?e=nyse&offset=0&count=100"
        elif market == "Tadawul":  # للسوق السعودي
            url = "https://finance.yahoo.com/quote/.TASI/components/"
        
        tables = pd.read_html(url)
        gainers_df = tables[0].copy()
        gainers_df['Market'] = market
        return gainers_df[['Symbol', 'Name', 'Price (Intraday)', '% Change', 'Volume', 'Market']]
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
        return pd.DataFrame()

def get_stock_data(symbol, period="1mo"):
    """جلب بيانات السهم من Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        if hist.empty:
            return pd.DataFrame()
        
        # تنظيف البيانات
        hist = hist[['Open', 'High', 'Low', 'Close', 'Volume']]
        hist.index = pd.to_datetime(hist.index)
        return hist
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
    
    market = st.selectbox("اختر السوق:", ["NASDAQ", "NYSE", "Tadawul"])
    
    if st.button("جلب أحدث البيانات"):
        with st.spinner(f"جاري تحليل الأسهم الأكثر ارتفاعًا في {market}..."):
            gainers_df = get_top_gainers_market(market)
            
            if not gainers_df.empty:
                # تحليل أول 10 أسهم فقط للأداء
                results = []
                for _, row in gainers_df.head(10).iterrows():
                    symbol = row['Symbol']
                    stock_data = get_stock_data(symbol)
                    
                    if not stock_data.empty and len(stock_data) > 20:
                        # حساب المؤشرات
                        stock_data['OBV'] = calculate_obv(stock_data)
                        stock_data['MFI'] = calculate_mfi(stock_data)
                        stock_data['Daily_Return'] = stock_data['Close'].pct_change() * 100
                        stock_data['Avg_Volume'] = stock_data['Volume'].rolling(20).mean()
                        
                        # تقييم آخر يومين
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
                            strength_emoji = "✅"
                        elif is_rising and high_volume and not obv_rising:
                            strength = "تحذير: OBV متناقض"
                            strength_emoji = "⚠️"
                        else:
                            strength = "ضعيف"
                            strength_emoji = "❌"
                        
                        results.append({
                            'السهم': symbol,
                            'الاسم': row['Name'],
                            'السوق': market,
                            'السعر': f"{last_day['Close']:.2f}",
                            'التغير %': f"{row['% Change']}",
                            'الحجم': f"{last_day['Volume']:,.0f}",
                            'OBV': "صاعد" if obv_rising else "هابط",
                            'MFI': f"{last_day['MFI']:.1f}",
                            'القوة': strength,
                            'الرمز': strength_emoji
                        })
                
                # عرض النتائج
                results_df = pd.DataFrame(results)
                st.dataframe(
                    results_df.sort_values('القوة', ascending=False),
                    column_config={
                        "الرمز": st.column_config.TextColumn("التقييم")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # عرض أفضل الأسهم
                st.subheader("أفضل الأسهم ذات المؤشرات القوية")
                strong_stocks = results_df[results_df['القوة'] == "قوي"]
                if not strong_stocks.empty:
                    for _, stock in strong_stocks.iterrows():
                        st.success(f"{stock['الرمز']} {stock['السهم']} ({stock['الاسم']}): سعر {stock['السعر']} (تغير {stock['التغير %']}) - حجم تداول {stock['الحجم']}")
                else:
                    st.warning("لا توجد أسهم ذات مؤشرات قوية اليوم")
            else:
                st.error("لا يمكن جلب بيانات الأسهم الأكثر ارتفاعًا")

with tab2:
    st.header("تحليل سهم معين")
    symbol = st.text_input("أدخل رمز السهم (مثال: AAPL, 2222.SR):", "AAPL")
    
    if st.button("تحليل السهم"):
        if not symbol:
            st.warning("الرجاء إدخال رمز السهم")
        else:
            with st.spinner(f"جاري تحليل سهم {symbol}..."):
                stock_data = get_stock_data(symbol, period="3mo")
                
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
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("السعر الأخير", f"{last_day['Close']:.2f}")
                        st.metric("حجم التداول", f"{last_day['Volume']:,.0f}")
                        
                    with col2:
                        st.metric("التغير اليومي", f"{stock_data['Daily_Return'].iloc[-1]:.2f}%")
                        st.metric("متوسط الحجم (20 يوم)", f"{last_day['Avg_Volume']:,.0f}")
                        
                    with col3:
                        st.metric("مؤشر OBV", "صاعد ▲" if last_day['OBV'] > prev_day['OBV'] else "هابط ▼")
                        st.metric("مؤشر MFI", f"{last_day['MFI']:.1f}")
                    
                    # تحليل القوة
                    st.subheader("تقييم قوة السهم")
                    
                    analysis_text = ""
                    if last_day['Close'] > prev_day['Close']:
                        analysis_text += "✅ السهم في اتجاه صاعد\n\n"
                        
                        if last_day['Volume'] > last_day['Avg_Volume']:
                            analysis_text += "✅ حجم التداول أعلى من المتوسط (قوة إضافية)\n\n"
                            
                            if last_day['OBV'] > prev_day['OBV']:
                                analysis_text += "✅ مؤشر OBV صاعد (تأكيد على قوة الاتجاه)\n\n"
                                
                                if 50 < last_day['MFI'] < 80:
                                    analysis_text += "✅ مؤشر MFI في النطاق الصحي (50-80)\n\n"
                                    st.success("إشارة شراء قوية: جميع المؤشرات إيجابية")
                                else:
                                    st.warning("تحذير: مؤشر MFI خارج النطاق المثالي")
                            else:
                                st.warning("⚠️ تحذير: السهم صاعد ولكن OBV هابط - ضعف محتمل في الاتجاه")
                        else:
                            st.warning("⚠️ تحذير: السهم صاعد ولكن بحجم تداول منخفض")
                    else:
                        st.error("❌ السهم ليس في اتجاه صاعد اليوم")
                    
                    st.text_area("تحليل مفصل", analysis_text, height=150)
                    
                    # الرسوم البيانية
                    st.subheader("الرسوم البيانية")
                    
                    fig1 = px.line(stock_data, x=stock_data.index, y='Close', 
                                 title=f"تحليل سعر سهم {symbol}")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    fig2 = px.line(stock_data, x=stock_data.index, y=['Volume', 'Avg_Volume'], 
                                 title=f"حجم التداول لسهم {symbol}",
                                 labels={'value': 'الحجم', 'variable': ''})
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    fig3 = px.line(stock_data, x=stock_data.index, y='OBV', 
                                 title=f"مؤشر OBV لسهم {symbol}")
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    fig4 = px.line(stock_data, x=stock_data.index, y='MFI', 
                                 title=f"مؤشر MFI لسهم {symbol}")
                    fig4.add_hline(y=50, line_dash="dash", line_color="gray")
                    fig4.add_hline(y=80, line_dash="dash", line_color="red")
                    st.plotly_chart(fig4, use_container_width=True)
                    
                else:
                    st.error("فشل في جلب بيانات السهم. الرجاء التحقق من رمز السهم")

# --- تذييل الصفحة ---
st.markdown("""
---
**ملاحظات مهمة:**
1. البيانات مقدمة من Yahoo Finance
2. التحليل للأغراض التعليمية فقط وليس نصيحة استثمارية
3. الأسعار متأخرة 15 دقيقة على الأقل للأسواق الأمريكية
""")
