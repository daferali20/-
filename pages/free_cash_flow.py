import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from telegram_sender import TelegramSender  # تأكد أن هذا الملف موجود

st.set_page_config(page_title="تحليل التدفق النقدي الحر", layout="wide")

# التحقق من إعدادات Alpha Vantage
if "alpha_vantage" not in st.secrets:
    st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
    st.stop()

api_key = st.secrets["alpha_vantage"]["api_key"]

# واجهة المستخدم
st.title("💰 تحليل الشركات حسب التدفق النقدي الحر (Free Cash Flow)")
symbols_input = st.text_input("🔍 أدخل رموز الأسهم (مثل: AAPL, MSFT, TSLA)", value="AAPL")

if st.button("📊 تحليل FCF"):
    symbols = [sym.strip().upper() for sym in symbols_input.split(",") if sym.strip()]
    
    results = []

    with st.spinner("جاري تحليل التدفقات النقدية..."):
        for symbol in symbols:
            url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={api_key}"
            response = requests.get(url)
            if response.status_code != 200:
                continue

            data = response.json()
            if "annualReports" not in data:
                continue

            reports = data["annualReports"]
            fcf_data = []
            for report in reports:
                try:
                    operating = int(report["operatingCashflow"])
                    capex = int(report["capitalExpenditures"])
                    fcf = operating - capex
                    fcf_data.append({
                        "symbol": symbol,
                        "fiscalDateEnding": report["fiscalDateEnding"],
                        "operatingCashflow": operating,
                        "capitalExpenditures": capex,
                        "freeCashFlow": fcf
                    })
                except:
                    continue

            if fcf_data:
                df = pd.DataFrame(fcf_data)
                results.append((symbol, df))

    if not results:
        st.warning("❌ لا توجد بيانات FCF متاحة.")
    else:
        for symbol, df in results:
            st.subheader(f"📈 {symbol} - Free Cash Flow Analysis")
            st.dataframe(df[["fiscalDateEnding", "freeCashFlow"]])

            st.line_chart(df.set_index("fiscalDateEnding")["freeCashFlow"])

        # زر إرسال إلى التليجرام
        if st.button("📩 إرسال النتائج إلى التليجرام"):
            try:
                msg = "💰 <b>تحليل التدفق النقدي الحر (FCF)</b>\n\n"
                for symbol, df in results:
                    msg += f"📊 <b>{symbol}</b>\n"
                    for _, row in df.iterrows():
                        fcf_m = round(row['freeCashFlow'] / 1e6, 2)
                        msg += f"- {row['fiscalDateEnding']}: ${fcf_m}M\n"
                    msg += "───────────────\n"
                msg += f"\n⏰ التوقيت: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                sender = TelegramSender()
                success = sender.send_message(msg)
                if success:
                    st.success("✅ تم إرسال النتائج إلى تليجرام بنجاح!")
                else:
                    st.error("❌ فشل في إرسال الرسالة.")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
