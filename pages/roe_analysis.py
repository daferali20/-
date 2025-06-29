import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
from telegram_sender import send_telegram_message

# زر لإرسال الرسالة
if st.button("📩 إرسال الأسهم المرتفعة إلى التليجرام"):
    message = "🚀 قائمة الأسهم الأمريكية الأكثر ارتفاعًا:\n"
    for i, row in gainers_df.iterrows():
        message += f"🔹 {row['ticker']} - ${row['price']} ({row['change_percentage']}%)\n"

    if send_telegram_message(message):
        st.success("✅ تم إرسال الرسالة إلى تليجرام بنجاح!")
    else:
        st.error("❌ فشل في إرسال الرسالة. تحقق من الإعدادات.")

def main():
    st.title("📊 تحليل الشركات حسب عائد حقوق المساهمين (ROE)")
    
    # التحقق من وجود API Key
    if "alpha_vantage" not in st.secrets:
        st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
        st.stop()
    
    api_key = st.secrets["alpha_vantage"]["api_key"]
    
    @st.cache_data(ttl=86400)  # تحديث البيانات كل 24 ساعة
    def fetch_roe_data():
        try:
            # جلب بيانات الشركات ذات أعلى ROE من API
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=MSFT&apikey={api_key}"
            # مثال لطلب متعدد (في التطبيق الفعلي تحتاج لطلبات متعددة أو API مختلف)
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data
            return None
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {str(e)}")
            return None
    
    # واجهة البحث
    st.sidebar.header("🔍 معايير البحث")
    min_roe = st.sidebar.slider("حدد أدنى عائد على حقوق المساهمين (ROE)%", 0, 50, 15)
    sector = st.sidebar.selectbox("اختر القطاع", [
        "الكل", "التكنولوجيا", "الطاقة", "الرعاية الصحية", 
        "الخدمات المالية", "السلع الاستهلاكية"
    ])
    
    # جلب وعرض البيانات
    if st.button("🔎 بحث عن الشركات"):
        with st.spinner("جاري تحليل البيانات..."):
            # محاكاة لجلب البيانات (في التطبيق الفعلي تستبدل بطلبات API حقيقية)
            sample_data = {
                "Symbol": ["AAPL", "MSFT", "JNJ", "XOM", "JPM"],
                "Company": ["Apple", "Microsoft", "Johnson & Johnson", "Exxon Mobil", "JPMorgan Chase"],
                "ROE": [147.3, 43.68, 25.19, 22.11, 16.57],
                "Sector": ["التكنولوجيا", "التكنولوجيا", "الرعاية الصحية", "الطاقة", "الخدمات المالية"],
                "MarketCap": ["2.8T", "2.5T", "450B", "440B", "480B"]
            }
            
            df = pd.DataFrame(sample_data)
            
            # تطبيق عوامل التصفية
            if sector != "الكل":
                df = df[df["Sector"] == sector]
            df = df[df["ROE"] >= min_roe]
            
            if not df.empty:
                st.success(f"تم العثور على {len(df)} شركة تلبي المعايير")
                
                # عرض النتائج في جدول
                st.subheader("📋 نتائج البحث")
                st.dataframe(
                    df.sort_values("ROE", ascending=False),
                    column_config={
                        "Symbol": "الرمز",
                        "Company": "الشركة",
                        "ROE": st.column_config.NumberColumn(
                            "عائد حقوق المساهمين %",
                            format="%.2f %%"
                        ),
                        "Sector": "القطاع",
                        "MarketCap": "القيمة السوقية"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
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
                
                # تحليل إضافي
                st.subheader("🧮 التحليل المالي")
                selected_company = st.selectbox(
                    "اختر شركة لعرض تفاصيل أكثر",
                    df["Company"].tolist()
                )
                
                if selected_company:
                    company_data = df[df["Company"] == selected_company].iloc[0]
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("عائد حقوق المساهمين", f"{company_data['ROE']:.2f}%")
                    
                    with col2:
                        st.metric("القيمة السوقية", company_data["MarketCap"])
                    
                    with col3:
                        st.metric("القطاع", company_data["Sector"])
                    
                    # هنا يمكنك إضافة المزيد من التحليل باستخدام API
            else:
                st.warning("⚠️ لا توجد شركات تلبي معايير البحث")
    
    # إضافة قسم التعليمات
    with st.expander("ℹ️ كيفية استخدام الأداة"):
        st.markdown("""
        ### دليل استخدام أداة تحليل ROE
        1. حدد الحد الأدنى لـ ROE باستخدام المنزلق
        2. اختر القطاع المطلوب (اختياري)
        3. اضغط على زر البحث
        4. استكشف النتائج والرسوم البيانية
        
        ### ما هو عائد حقوق المساهمين (ROE)؟
        - مقياس للربحية يحسب نسبة صافي الدخل إلى حقوق المساهمين
        - يعبر عن كفاءة الشركة في تحقيق الأرباح من استثمارات المساهمين
        - كلما ارتفعت النسبة، كانت الشركة أكثر كفاءة في تحقيق الأرباح
        """)

if __name__ == "__main__":
    main()
