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

# طريقة تشغيل الصفحة الرئيسية
def safe_main():
    try:
        # التحقق من وجود الملف أولاً
        if os.path.exists("pages/us_market.py"):
            from pages.us_market import main
            
            # إضافة معالجة الأخطاء للوظيفة الرئيسية
            try:
                main()
            except KeyError as ke:
                st.error(f"خطأ في بنية البيانات: {str(ke)}")
                st.info("قد يكون هناك تغيير في هيكل البيانات الواردة من المصدر")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {str(e)}")
        else:
            st.error("ملف الصفحة الرئيسية غير موجود")
    except ImportError:
        st.error("تعذر استيراد وحدة الصفحة الرئيسية")
    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
        if st.button("حاول مرة أخرى"):
            st.rerun()

# تشغيل الوظيفة الآمنة
safe_main()
