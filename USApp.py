import streamlit as st
from datetime import datetime
import pytz
import os
import sys

# إعدادات عامة للتطبيق
st.set_page_config(
    page_title="نظام تحليل السوق الأمريكي",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# إضافة خيارات التنقل
selected_page = st.sidebar.radio(
    "اختر الصفحة:",
    ["اللوحة الرئيسية", "تحليل ROE", "الأسهم المفضلة"]
)

# طريقة تشغيل الصفحات
try:
    if selected_page == "اللوحة الرئيسية":
        if os.path.exists("pages/us_market.py"):
            # إضافة المسار إلى sys.path للاستيراد الصحيح
            sys.path.insert(0, os.path.abspath('.'))
            from pages.us_market import main as market_main
            market_main()
        else:
            st.error("ملف اللوحة الرئيسية غير موجود")
    
    elif selected_page == "تحليل ROE":
        if os.path.exists("pages/roe_analysis.py"):
            sys.path.insert(0, os.path.abspath('.'))
            from pages.roe_analysis import main as roe_main
            roe_main()
        else:
            st.error("ملف تحليل ROE غير موجود")
    
    elif selected_page == "الأسهم المفضلة":
        st.info("هذه الميزة قيد التطوير")

except Exception as e:
    st.error(f"حدث خطأ غير متوقع: {str(e)}")
    st.write("تفاصيل الخطأ:", e)
    
    if st.button("حاول مرة أخرى"):
        st.rerun()

# تذييل الصفحة
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p>تم التطوير بواسطة فريق التحليل المالي</p>
    <p>© 2023 جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)
