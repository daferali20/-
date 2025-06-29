import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from telegram_sender import TelegramSender

def fetch_roe_for_symbols(symbols, api_key):
    data_list = []
    for symbol in symbols:
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()
                # تأكد أن ROE موجودة ويمكن تحويله إلى float
                roe = float(json_data.get("ReturnOnEquityTTM", 0))
                data_list.append({
                    "Symbol": symbol,
                    "Company": json_data.get("Name", "Unknown"),
                    "ROE": roe * 100,  # تحويل من نسبة عشرية إلى %
                    "Sector": json_data.get("Sector", "Unknown"),
                    "MarketCap": json_data.get("MarketCapitalization", "Unknown")
                })
            else:
                st.warning(f"تعذر جلب بيانات {symbol}")
        except Exception as e:
            st.warning(f"خطأ في جلب بيانات {symbol}: {e}")

    return pd.DataFrame(data_list)

def main():
    st.title("📊 تحليل الشركات حسب عائد حقوق المساهمين (ROE)")

    if "alpha_vantage" not in st.secrets:
        st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
        st.stop()

    if "telegram" not in st.secrets:
        st.error("⚠️ إعدادات Telegram غير موجودة في secrets.toml")
        st.stop()

    api_key = st.secrets["alpha_vantage"]["api_key"]

    st.sidebar.header("🔍 معايير البحث")
    min_roe = st.sidebar.slider("حدد أدنى عائد على حقوق المساهمين (ROE)%", 0, 50, 15)
    sector = st.sidebar.selectbox("اختر القطاع", [
        "الكل", "التكنولوجيا", "الطاقة", "الرعاية الصحية",
        "الخدمات المالية", "السلع الاستهلاكية"
    ])

    # قائمة الأسهم التي تريد تحليلها (يمكنك تعديلها)
    symbols = ["AAPL", "MSFT", "JNJ", "XOM", "JPM"]

    if st.button("🔎 بحث عن الشركات"):
        with st.spinner("جاري جلب وتحليل البيانات..."):
            df = fetch_roe_for_symbols(symbols, api_key)

            # تصفية البيانات
            if sector != "الكل":
                df = df[df["Sector"] == sector]
            df = df[df["ROE"] >= min_roe]

            st.session_state["search_results"] = df

    # عرض النتائج
    if "search_results" in st.session_state:
        df = st.session_state["search_results"]

        if not df.empty:
            st.success(f"تم العثور على {len(df)} شركة تلبي المعايير")
            st.subheader("📋 نتائج البحث")
            st.dataframe(df)

            st.subheader("📈 توزيع ROE حسب القطاع")
            fig = px.bar(
                df,
                x="Company",
                y="ROE",
                color="Sector",
                text="ROE",
                labels={"ROE": "عائد حقوق المساهمين %", "Company": "الشركة"}
            )
            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

            if st.button("📩 إرسال نتائج ROE إلى التليجرام"):
                try:
                    message = f"📊 <b>نتائج تحليل ROE</b>\n\n"
                    message += f"<b>معايير البحث:</b>\n"
                    message += f"- أدنى ROE: {min_roe}%\n"
                    message += f"- القطاع: {sector}\n\n"
                    message += f"<b>الشركات التي تطابق المعايير ({len(df)}):</b>\n\n"

                    for _, row in df.iterrows():
                        message += f"🏢 <b>{row['Company']}</b> ({row['Symbol']})\n"
                        message += f"📊 ROE: {row['ROE']:.2f}%\n"
                        message += f"🏛 القطاع: {row['Sector']}\n"
                        message += f"💰 القيمة السوقية: {row['MarketCap']}\n"
                        message += "────────────────────\n"

                    message += f"\n🔄 آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

                    sender = TelegramSender()
                    success = sender.send_message(message)

                    if success:
                        st.success("✅ تم إرسال النتائج إلى تليجرام بنجاح!")
                    else:
                        st.error("❌ فشل في إرسال الرسالة. يرجى التحقق من إعدادات Telegram.")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الإرسال: {e}")

        else:
            st.warning("⚠️ لا توجد شركات تلبي معايير البحث.")

    with st.expander("ℹ️ كيفية استخدام الأداة"):
        st.markdown("""
        ### دليل الاستخدام
        - حدد حدًا أدنى لـ ROE
        - اختر قطاعًا (اختياري)
        - اضغط على "بحث"
        - ثم يمكنك إرسال النتائج مباشرة إلى تليجرام
        """)

if __name__ == "__main__":
    main()
