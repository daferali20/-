import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from telegram_sender import TelegramSender

st.set_page_config(page_title="تحليل التدفق النقدي الحر - Finnhub", layout="wide")

# التحقق من إعدادات Finnhub
if "finnhub" not in st.secrets:
    st.error("⚠️ إعدادات Finnhub غير موجودة في secrets.toml")
    st.stop()

api_key = st.secrets["finnhub"]["api_key"]

# واجهة المستخدم
st.title("💰 تحليل الشركات حسب التدفق النقدي الحر (FCF) - باستخدام Finnhub")
symbols_input = st.text_input("🔍 أدخل رموز الأسهم (مثل: AAPL, MSFT, TSLA)", value="AAPL")

# عند الضغط على زر تحليل
if st.button("📊 تحليل FCF"):
    symbols = [sym.strip().upper() for sym in symbols_input.split(",") if sym.strip()]
    results = []

    with st.spinner("⏳ جاري تحليل التدفقات النقدية..."):
        for symbol in symbols:
            url = f"https://finnhub.io/api/v1/stock/financials?symbol={symbol}&statement=cf&freq=annual&token={api_key}"
            response = requests.get(url)
            if response.status_code != 200:
                st.warning(f"⚠️ لم يتم جلب بيانات {symbol}")
                continue

            data = response.json()
            if "data" not in data or not data["data"]:
                st.warning(f"⚠️ لا توجد بيانات مالية لـ {symbol}")
                continue

            # نحسب FCF = Operating Cash Flow - Capital Expenditure
            rows = []
            for report in data["data"]:
                try:
                    op = float(report.get("cashFromOperations", 0))
                    capex = float(report.get("capitalExpenditures", 0))
                    fcf = op - capex
                    rows.append({
                        "fiscalDate": report["year"],
                        "OperatingCashFlow": op,
                        "CapitalExpenditures": capex,
                        "FreeCashFlow": fcf
                    })
                except:
                    continue

            if rows:
                df = pd.DataFrame(rows)
                results.append((symbol, df))

    if not results:
        st.warning("❌ لا توجد بيانات FCF متاحة.")
    else:
        message = "💰 <b>تحليل التدفق النقدي الحر (FCF)</b>\n\n"
        for symbol, df in results:
            st.subheader(f"📈 {symbol} - التحليل")
            st.markdown(f"[🔗 تفاصيل السهم على Finnhub](https://finnhub.io/stock/{symbol})", unsafe_allow_html=True)

            st.dataframe(df)
            st.line_chart(df.set_index("fiscalDate")["FreeCashFlow"])

            message += f"📊 <b>{symbol}</b>\n"
            for _, row in df.iterrows():
                fcf_m = round(row['FreeCashFlow'] / 1e6, 2)
                message += f"- {row['fiscalDate']}: ${fcf_m}M\n"
            message += f"🔗 https://finnhub.io/stock/{symbol}\n"
            message += "───────────────\n"

        message += f"\n⏰ التوقيت: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        if st.button("📩 إرسال النتائج إلى تليجرام"):
            try:
                sender = TelegramSender()
                success = sender.send_message(message)
                if success:
                    st.success("✅ تم إرسال النتائج إلى تليجرام بنجاح!")
                else:
                    st.error("❌ فشل في إرسال الرسالة.")
            except Exception as e:
                st.error(f"❌ خطأ أثناء الإرسال: {e}")
