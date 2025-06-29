import streamlit as st
from telegram_sender import TelegramSender

def main():
    st.title("اختبار إرسال رسالة إلى تليجرام")

    message = st.text_area("اكتب رسالة للإرسال:", "مرحبا! هذه رسالة اختبار من Streamlit.")

    if st.button("إرسال إلى تليجرام"):
        sender = TelegramSender()
        success = sender.send_message(message)
        if success:
            st.success("تم إرسال الرسالة بنجاح!")
        else:
            st.error("فشل في إرسال الرسالة. تحقق من إعدادات التوكن والـ chat_id.")

if __name__ == "__main__":
    main()
