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

    # تقسيم الشركات إلى رسائل متعددة (كل 10 شركات في رسالة)
    messages = []
    companies_per_message = 10

    filtered = filtered.reset_index(drop=True)
    total = len(filtered)

    for i in range(0, total, companies_per_message):
        chunk = filtered.iloc[i:i + companies_per_message]
        message = f"📊 الشركات الجيدة حسب التحليل ({i+1} - {min(i+companies_per_message, total)}):\n\n"

        for _, row in chunk.iterrows():
            symbol = row['symbol']
            name = row['companyName']
            price = row['price']
            dividend = row['lastAnnualDividend']

            message += f"🔹 {symbol} - {name}\n"
            message += f"     💲 السعر: {price:,.2f}\n"
            message += f"     💰 التوزيع: {dividend:,.2f}\n\n"

        message += "📡 تم الإرسال من النظام."
        messages.append(message)

    # إرسال إلى تيليجرام
    if st.button("📨 إرسال النتائج إلى Telegram"):
        sender = TelegramSender()
        success_count = 0
        for msg in messages:
            result = sender.send_message(msg)
            if result and isinstance(result, dict) and result.get("ok"):
                success_count += 1
        if success_count == len(messages):
            st.success(f"✅ تم إرسال جميع الرسائل ({success_count}) بنجاح!")
        else:
            st.warning(f"⚠️ تم إرسال {success_count} من {len(messages)} رسالة.")
