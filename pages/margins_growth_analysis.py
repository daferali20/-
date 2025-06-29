import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from telegram_sender import TelegramSender

st.set_page_config(page_title="تحليل الهوامش والنمو - Finnhub", layout="wide")

# التحقق من إعدادات Finnhub
if "finnhub" not in st.secrets:
    st.error("⚠️ إعدادات Finnhub غير موجودة في secrets.toml")
    st.stop()

api_key = st.secrets["finnhub"]["api_key"]

# إدخال رموز الأسهم
st.title("📊 تحليل الهوامش والنمو")
symbols_input = st.text_input("🔍 أدخل رموز الأسهم (مثل: AAPL, MSFT, TSLA)", value="AAPL")

if st.button("📊 تحليل البيانات"):
    symbols = [sym.strip().upper() for sym in symbols_input.split(",") if sym.strip()]
    results = []

    with st.spinner("جاري تحليل الهوامش والنمو..."):
        for symbol in symbols:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={api_key}"
            response = requests.get(url)

            if response.status_code != 200:
                st.warning(f"⚠️ لم يتم جلب البيانات لـ {symbol}")
                continue

            data = response.json()
            metrics = data.get("metric", {})

            if not metrics:
                st.warning(f"⚠️ لا توجد بيانات متاحة لـ {symbol}")
                continue

            try:
                op_margin = float(metrics.get("operatingMarginTTM", "nan")) * 100
                net_margin = float(metrics.get("netProfitMarginTTM", "nan")) * 100
                revenue_growth = float(metrics.get("revenueGrowthTTM", "nan")) * 100

                results.append({
                    "Symbol": symbol,
                    "Operating Margin (%)": round(op_margin, 2),
                    "Net Profit Margin (%)": round(net_margin, 2),
                    "Revenue Growth (%)": round(revenue_growth, 2),
                    "Finnhub Link": f"https://finnhub.io/stock/{symbol}"
                })
            except:
                st.warning(f"⚠️ تعذر تحليل البيانات لـ {symbol}")

    if not results:
        st.error("❌ لم يتم العثور على بيانات.")
    else:
        df = pd.DataFrame(results)
        st.subheader("📋 النتائج")
        st.dataframe(df)

        # 📩 إرسال إلى تليجرام
        if st.button("📩 إرسال التقرير إلى تليجرام"):
            try:
                message = "📊 <b>تقرير الهوامش والنمو</b>\n\n"
                for row in results:
                    message += f"📈 <b>{row['Symbol']}</b>\n"
                    message += f"🔹 Operating Margin: {row['Operating Margin (%)']}%\n"
                    message += f"🔹 Net Profit Margin: {row['Net Profit Margin (%)']}%\n"
                    message += f"🔹 Revenue Growth: {row['Revenue Growth (%)']}%\n"
                    message += f"🔗 {row['Finnhub Link']}\n"
                    message += "───────────────\n"
                message += f"\n⏰ التوقيت: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                sender = TelegramSender()
                success = sender.send_message(message)
                if success:
                    st.success("✅ تم إرسال التقرير إلى تليجرام بنجاح!")
                else:
                    st.error("❌ فشل في إرسال التقرير.")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الإرسال: {e}")
