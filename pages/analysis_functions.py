import streamlit as st
from analysis_functions import fetch_tradingview_chart, preprocess_chart_image, detect_chart_patterns

st.title("نظام التحليل الفني المتقدم - الذكاء الاصطناعي")

tickers_input = st.text_area("أدخل رموز الأسهم (سطر لكل سهم)")
timeframe = st.selectbox("اختر الإطار الزمني", ["1 يوم", "1 أسبوع", "1 شهر", "4 ساعات", "1 ساعة"])

if st.button("تحليل"):
    tickers = [t.strip().upper() for t in tickers_input.splitlines() if t.strip()]
    for ticker in tickers:
        try:
            chart_img = fetch_tradingview_chart(ticker, timeframe)
            st.image(chart_img, caption=f"الشارت الفني للسهم {ticker}")
            processed_img = preprocess_chart_image(chart_img)
            patterns = detect_chart_patterns(processed_img)
            st.write(f"الأنماط المكتشفة للسهم {ticker}: {patterns}")
        except Exception as e:
            st.error(f"حدث خطأ في تحليل السهم {ticker}: {str(e)}")
