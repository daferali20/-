import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from telegram_sender import send_telegram_message

def main():
    st.title("📊 تحليل الشركات حسب عائد حقوق المساهمين (ROE)")

    # التحقق من وجود API Key
    if "alpha_vantage" not in st.secrets:
        st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
        st.stop()

    api_key = st.secrets["alpha_vantage"]["api_key"]

    @st.cache_data(ttl=86400)
    def fetch_roe_data():
        # جلب بيانات شركة واحدة كمثال (يمكنك توسيعها لاحقًا)
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=MSFT&apikey={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {str(e)}")
            return None

    # واجهة المستخدم
    st.sidebar.header("🔍 معايير البحث")
    min_roe = st.sidebar.slider("حدد أدنى عائد على حقوق المساهمين (ROE)%", 0, 50, 15)
    sector = st.sidebar.selectbox("اختر القطاع", [
        "الكل", "التكنولوجيا", "الطاقة", "الرعاية الصحية", 
        "الخدمات المالية", "السلع الاستهلاكية"
    ])

    # زر البحث
    if st.button("🔎 بحث عن الشركات"):
        with st.spinner("جاري تحليل البيانات..."):
            # بيانات وهمية مؤقتًا
            sample_data = {
                "Symbol": ["AAPL", "MSFT", "JNJ", "XOM", "JPM"],
                "Company": ["Apple", "Microsoft", "Johnson & Johnson", "Exxon Mobil", "JPMorgan Chase"],
                "ROE": [147.3, 43.68, 25.19, 22.11, 16.57],
                "Sector": ["التكنولوجيا", "التكنولوجيا", "الرعاية الصحية", "الطاقة", "الخدمات المالية"],
                "MarketCap": ["2.8T", "2.5T", "450B", "440B", "480B"]
            }

            df = pd.DataFrame(sample_data)

            # تصفية البيانات
            if sector != "الكل":
                df = df[df["Sector"] == sector]
            df = df[df["ROE"] >= min_roe]

            if not df.empty:
                st.success(f"تم العثور على {len(df)} شركة تلبي المعايير")
                st.subheader("📋 نتائج البحث")
                st.dataframe(df)

                # رسم بياني
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

                # 📩 زر إرسال النتائج إلى Telegram
                if st.button("📩 إرسال نتائج ROE إلى التليجرام"):
                    message = "📊 <b>قائمة الشركات ذات ROE مرتفع:</b>\n"
                    for i, row in df.iterrows():
                        message += f"🔹 <b>{row['Company']}</b> ({row['Symbol']}) - ROE: {row['ROE']}%\n"
                    
                    if send_telegram_message(message):
                        st.success("✅ تم إرسال النتائج إلى تليجرام.")
                    else:
                        st.error("❌ فشل في إرسال الرسالة.")

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
