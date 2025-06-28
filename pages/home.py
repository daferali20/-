import streamlit as st

def home_page():
    st.set_page_config(page_title="الصفحة الرئيسية", layout="wide")
    st.title("🏠 الصفحة الرئيسية")

    st.write("""
    مرحباً بكم في نظام تحليل الأسواق المالية المتكامل.
    """)

    col1 = st.columns(1)[0]  # ← تصحيح هنا

    with col1:
        st.info("""
        **السوق الأمريكي:**
        - المؤشرات الرئيسية
        - الأسهم الأكثر نشاطاً
        - الأخبار الاقتصادية
        """)
