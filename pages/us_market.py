# ملف pages/us_market.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

st.set_page_config(page_title="نظرة على السوق الأمريكي", layout="wide")
st.title("📈 نظرة شاملة على السوق الأمريكي")


@st.cache_data(ttl=3600)
def fetch_us_market_data():
    try:
        # بيانات وهمية للقطاعات الأمريكية الرئيسية
        sectors = [
            "التكنولوجيا", "الطاقة", "الصحة", "التمويل", 
            "اشباه الموصلات", "السلع الاستهلاكية", "الخدمات", "المرافق"
        ]
        
        sectors_data = []
        for sector in sectors:
            sectors_data.append({
                "name": sector,
                "change_percent": round(random.uniform(-2.0, 2.5), 2),
                "volume": random.randint(50000000, 200000000),
                "market_cap": random.uniform(500000000000, 3000000000000),
                "pe_ratio": round(random.uniform(10, 35), 2),
                "dividend_yield": round(random.uniform(0.5, 4.5), 2),
                "performance_week": round(random.uniform(-5, 5), 2),
                "performance_month": round(random.uniform(-10, 10), 2)
            })
        
        return pd.DataFrame(sectors_data)
    
    except Exception as e:
        st.error(f"فشل في جلب البيانات: {str(e)}")
        return None

# جلب البيانات
sectors_df = fetch_us_market_data()

if sectors_df is not None:
    # عرض نظرة عامة على القطاعات
    st.markdown("## 📈 نظرة عامة على القطاعات")
    
    # عرض جدول القطاعات
    st.dataframe(sectors_df[['name', 'change_percent', 'volume', 'market_cap', 'pe_ratio', 'dividend_yield']]
                 .sort_values('change_percent', ascending=False)
                 .rename(columns={
                     'name': 'القطاع',
                     'change_percent': 'التغير %',
                     'volume': 'حجم التداول',
                     'market_cap': 'القيمة السوقية (مليار)',
                     'pe_ratio': 'نسبة P/E',
                     'dividend_yield': 'عائد التوزيعات %'
                 }), 
                 height=400)
    
    # عرض رسوم بيانية للقطاعات
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure(go.Bar(
            x=sectors_df['change_percent'],
            y=sectors_df['name'],
            orientation='h',
            marker_color=['green' if x > 0 else 'red' for x in sectors_df['change_percent']]
        ))
        fig1.update_layout(title="أداء القطاعات اليوم", 
                          xaxis_title="نسبة التغير %", 
                          yaxis_title="القطاع")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = go.Figure(go.Pie(
            labels=sectors_df['name'],
            values=sectors_df['market_cap'],
            hole=.3
        ))
        fig2.update_layout(title="توزيع القيمة السوقية للقطاعات")
        st.plotly_chart(fig2, use_container_width=True)
    
    # أداء القطاعات خلال الأسبوع والشهر
    st.markdown("## 📆 أداء القطاعات خلال الفترات الزمنية")
    
    fig3 = go.Figure()
    for idx, row in sectors_df.iterrows():
        fig3.add_trace(go.Scatter(
            x=['الأسبوع', 'الشهر'],
            y=[row['performance_week'], row['performance_month']],
            name=row['name'],
            mode='lines+markers'
        ))
    
    fig3.update_layout(title="أداء القطاعات خلال الأسبوع والشهر",
                      yaxis_title="نسبة التغير %",
                      xaxis_title="الفترة الزمنية")
    st.plotly_chart(fig3, use_container_width=True)
    
    # تحليل القطاع الأفضل أداءً
    best_sector = sectors_df.loc[sectors_df['change_percent'].idxmax()]
    st.markdown(f"### 🏆 أفضل قطاع أداءً اليوم: {best_sector['name']}")
    st.write(f"- نسبة التغير: {best_sector['change_percent']}%")
    st.write(f"- حجم التداول: {best_sector['volume']:,} سهم")
    st.write(f"- القيمة السوقية: ${best_sector['market_cap']/1000000000:,.1f} مليار")
    st.write(f"- نسبة P/E: {best_sector['pe_ratio']}")
    st.write(f"- عائد التوزيعات: {best_sector['dividend_yield']}%")
    
    # مقارنة بين القطاعات
    st.markdown("## 🔍 مقارنة بين القطاعات")
    selected_sectors = st.multiselect(
        "اختر قطاعات للمقارنة",
        options=sectors_df['name'].tolist(),
        default=["التكنولوجيا", "اشباه الموصلات", "الطاقة", "الصحة"]
    )
    
    if selected_sectors:
        filtered_df = sectors_df[sectors_df['name'].isin(selected_sectors)]
        
        fig4 = go.Figure()
        
        fig4.add_trace(go.Bar(
            x=filtered_df['name'],
            y=filtered_df['change_percent'],
            name='التغير اليومي %',
            marker_color='lightblue'
        ))
        
        fig4.add_trace(go.Scatter(
            x=filtered_df['name'],
            y=filtered_df['performance_week'],
            name='أداء الأسبوع %',
            mode='lines+markers',
            line=dict(color='orange', width=2)
        ))
        
        fig4.update_layout(title="مقارنة أداء القطاعات",
                          yaxis_title="نسبة التغير %",
                          barmode='group')
        st.plotly_chart(fig4, use_container_width=True)

else:
    st.error("لا يمكن عرض البيانات حالياً. يرجى المحاولة لاحقاً.")

st.markdown("---")
st.markdown("""
**ملاحظة:** هذا تطبيق تجريبي. لتنفيذ تطبيق حقيقي:
1. تحتاج لتفعيل واجهة برمجة التطبيقات (API) من مصدر موثوق مثل Yahoo Finance أو Alpha Vantage
2. إضافة المزيد من المقاييس التحليلية لكل قطاع
3. تحسين واجهة المستخدم لتوفير المزيد من خيارات التحليل
""")
