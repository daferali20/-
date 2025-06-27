import streamlit as st
from datetime import datetime
import pytz
import os

# إعدادات عامة للتطبيق
st.set_page_config(
    page_title="نظام تحليل السوق الأمريكي",
    layout="wide",
    initial_sidebar_state="expanded"
)

# التحقق من وجود ملف الصفحة
PAGE_PATH = "pages/us_market.py"
if not os.path.exists(PAGE_PATH):
    st.error(f"ملف الصفحة {PAGE_PATH} غير موجود")
    st.stop()

# عنوان التطبيق الرئيسي
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #2e86c1;">📈 نظام تحليل السوق الأمريكي</h1>
    <p>أداة متكاملة لتحليل مؤشرات وأسهم السوق الأمريكي</p>
</div>
""", unsafe_allow_html=True)

# شريط جانبي للتنقل
st.sidebar.title("🔍 القائمة الرئيسية")
st.sidebar.markdown("---")

# قسم معلومات التطبيق
last_update = datetime.now(pytz.timezone('America/New_York')).strftime("%Y-%m-%d %H:%M")
st.sidebar.info(f"""
**معلومات التطبيق:**
- الإصدار: 2.0
- تحديث البيانات: كل 30 دقيقة
- آخر تحديث: {last_update} (توقيت نيويورك)
""")

# طريقة بديلة أكثر أمانًا للتحويل
try:
    from us_market import main  # استيراد مباشر بدل switch_page
    main()
except ImportError:
    st.error("تعذر تحميل وحدة السوق الأمريكي")
    if st.button("حاول مرة أخرى"):
        st.rerun()
