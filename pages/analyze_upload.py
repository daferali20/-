import streamlit as st
import pandas as pd
from telegram_sender import TelegramSender

st.set_page_config(page_title="📤 تحليل ملف شركات", layout="wide")
st.title("📤 رفع ملف CSV وتحليل الشركات")

# رفع الملف
uploaded_file = st.file_uploader("📎 اختر ملف CSV يحتوي على بيانات الشركات", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 معاينة أول 5 أسطر")
    st.dataframe(df.head())

    # معالجة وتحويل الأعمدة المهمة
    for col in ["marketCap", "price", "lastAnnualDividend"]:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce")

    # تصفية الشركات الجيدة
    filtered = df[
        (df["marketCap"] > 1_000_000_000) &
        (df["price"] > 5) &
        (df["lastAnnualDividend"] > 0) &
        (df["isEtf"] == False) &
        (df["isFund"] == False) &
        (df["isActivelyTrading"] == True)
    ]

    st.success(f"✅ تم العثور على {len(filtered)} شركة جيدة.")
    st.dataframe(filtered[["symbol", "companyName", "price", "marketCap", "lastAnnualDividend"]])

    # توليد الرسالة
    message = "📊 الشركات الجيدة حسب التحليل:\n\n"
    for _, row in filtered.head(10).iterrows():
        message += f"🔹 {row['symbol']} - {row['companyName']} | السعر: {row['price']} | التوزيع: {row['lastAnnualDividend']}\n"
    message += "\n📡 تم الإرسال من النظام."

    # إرسال إلى تيليجرام
    if st.button("📨 إرسال النتائج إلى Telegram"):
        sender = TelegramSender()
        result = sender.send_message(message)
        if result and isinstance(result, dict) and result.get("ok"):
            st.success("✅ تم إرسال الرسالة بنجاح!")
        else:
            st.error("❌ فشل في إرسال الرسالة.")
