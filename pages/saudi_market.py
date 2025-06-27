# ملف pages/saudi_market.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="مؤشر الخوف السعودي", layout="centered")

st.title("📉 مؤشر الخوف في السوق السعودي (SFI)")

# توليد بيانات وهمية تماثل الوضع الحقيقي
down_ratio = random.uniform(0.2, 0.9)  # نسبة الأسهم الهابطة
volume_ratio = random.uniform(0.4, 1.0)  # حجم التداول الحالي مقابل المتوسط
big_sell_ratio = random.uniform(0.1, 0.6)  # نسبة أوامر البيع الكبيرة
tasi_drop = random.uniform(-2.5, 0.0)  # نسبة نزول مؤشر TASI
volatility_score = random.uniform(0, 1)  # تقلب الأسعار اللحظي

# حساب مؤشر الخوف
fear_score = (
    down_ratio * 30 +
    (1 - volume_ratio) * 20 +
    big_sell_ratio * 20 +
    abs(tasi_drop) * 8 +
    volatility_score * 10
)
fear_score = min(round(fear_score, 2), 100)

# تفسير النتيجة
if fear_score < 25:
    sentiment = "🟢 السوق مطمئن جدًا"
elif fear_score < 50:
    sentiment = "🟢 السوق مستقر"
elif fear_score < 75:
    sentiment = "🟠 قلق في السوق"
else:
    sentiment = "🔴 خوف شديد في السوق"

# عرض المؤشر
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=fear_score,
    title={'text': "مؤشر الخوف السعودي (SFI)", 'font': {'size': 24}},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "red"},
        'steps': [
            {'range': [0, 25], 'color': "lightgreen"},
            {'range': [25, 50], 'color': "green"},
            {'range': [50, 75], 'color': "orange"},
            {'range': [75, 100], 'color': "red"},
        ]
    }
))

st.plotly_chart(fig, use_container_width=True)
st.markdown(f"### 🧠 تحليل: {sentiment}")

# عرض التفاصيل الافتراضية
with st.expander("تفاصيل الحساب (بيانات تجريبية)"):
    st.write(f"🔻 نسبة الأسهم الهابطة: `{down_ratio:.2f}`")
    st.write(f"📉 نسبة انخفاض التداول: `{(1 - volume_ratio):.2f}`")
    st.write(f"💰 نسبة البيع الكبير: `{big_sell_ratio:.2f}`")
    st.write(f"📊 نزول المؤشر العام: `{tasi_drop:.2f}%`")
    st.write(f"⚡ تقلب الأسعار اللحظي: `{volatility_score:.2f}`")

