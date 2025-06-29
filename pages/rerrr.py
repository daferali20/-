import streamlit as st
import requests

def send_test_message():
    token = st.secrets["telegram"]["bot_token"]
    chat_id = st.secrets["telegram"]["chat_id"]
    message = "📢 اختبار إرسال من Streamlit إلى تليجرام"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        st.write(f"Response status: {response.status_code}")
        st.write(response.json())
        if response.status_code == 200:
            st.success("تم الإرسال بنجاح")
        else:
            st.error("فشل الإرسال")
    except Exception as e:
        st.error(f"خطأ: {str(e)}")

if st.button("إرسال رسالة اختبار"):
    send_test_message()
