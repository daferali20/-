# ملف app.py
import streamlit as st

# إعدادات عامة للتطبيق
st.set_page_config(
    page_title="نظام تحليل الأسواق المالية",
    layout="wide",
    initial_sidebar_state="expanded"
)

# عنوان التطبيق الرئيسي
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #2e86c1;">🏦 نظام تحليل الأسواق المالية</h1>
    <p>أداة متكاملة لتحليل مؤشرات الأسواق السعودية والأمريكية</p>
</div>
""", unsafe_allow_html=True)

# شريط جانبي للتنقل
st.sidebar.title("🔍 قائمة التنقل")
st.sidebar.markdown("---")

# اختيار السوق
market = st.sidebar.radio(
    "اختر السوق للتحليل:",
    ["السوق السعودي", "السوق الأمريكي"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**معلومات التطبيق:**
- إصدار 1.0
- بيانات السوق يتم تحديثها كل ساعة
- آخر تحديث: {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")))

# تحميل الصفحة المحددة
if market == "السوق السعودي":
    st.switch_page("pages/saudi_market.py")
elif market == "السوق الأمريكي":
    st.switch_page("pages/us_market.py")
