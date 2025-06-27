import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
# ملف pages/us_market.py
# إعدادات الصفحة
st.set_page_config(page_title="نظرة على السوق الأمريكي", layout="wide")
st.title("📈 نظرة شاملة على السوق الأمريكي")

# API Key لـ Alpha Vantage (يمكن الحصول على مفتاح مجاني من موقعهم)
#ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "YOUR_DEFAULT_API_KEY")
@st.cache_data(ttl=3600)
def fetch_market_data():
    try:
        # الوصول إلى المفاتيح من secrets.toml
        api_key = st.secrets["alpha_vantage"]["api_key"]
        api_url = st.secrets["alpha_vantage"]["api_url"]
        
        # مثال لاستخدام API
        url = f"{api_url}?function=TOP_GAINERS_LOSERS&apikey={api_key}"
        response = requests.get(url)
        # ... معالجة البيانات
        
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
#@st.cache_data(ttl=3600)
#def fetch_market_data():
 #   """جلب بيانات السوق من Alpha Vantage"""
  #  data = {
  #      "indices": {},
  #      "stocks": {},
  #      "news": []
  #  }
    
    try:
        # 1. جلب بيانات المؤشرات الرئيسية
        indices = ["DJIA", "SPX", "NDX", "RUT"]  # داو جونز، S&P 500، ناسداك، راسل 2000
        for index in indices:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={index}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                data["indices"][index] = response.json().get("Global Quote", {})
        
        # 2. جلب الأسهم الأكثر ارتفاعاً (بيانات وهمية لأغراض العرض)
        data["stocks"]["gainers"] = [
            {"symbol": "AAPL", "name": "Apple Inc", "price": 185.32, "change": 4.25, "change_percent": 2.35, "volume": 25000000},
            {"symbol": "TSLA", "name": "Tesla Inc", "price": 245.67, "change": 8.12, "change_percent": 3.42, "volume": 18000000},
            {"symbol": "NVDA", "name": "NVIDIA Corp", "price": 678.90, "change": 22.45, "change_percent": 3.42, "volume": 15000000},
            {"symbol": "AMZN", "name": "Amazon.com", "price": 175.45, "change": 3.67, "change_percent": 2.14, "volume": 12000000},
            {"symbol": "META", "name": "Meta Platforms", "price": 485.32, "change": 10.25, "change_percent": 2.16, "volume": 8000000}
        ]
        
        # 3. جلب الأسهم الأكثر تداولاً (بيانات وهمية)
        data["stocks"]["most_active"] = [
            {"symbol": "AAPL", "name": "Apple Inc", "price": 185.32, "change": 4.25, "change_percent": 2.35, "volume": 45000000},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "price": 165.78, "change": -2.45, "change_percent": -1.46, "volume": 42000000},
            {"symbol": "F", "name": "Ford Motor", "price": 12.45, "change": 0.25, "change_percent": 2.05, "volume": 38000000},
            {"symbol": "T", "name": "AT&T", "price": 16.78, "change": -0.12, "change_percent": -0.71, "volume": 35000000},
            {"symbol": "PLTR", "name": "Palantir Tech", "price": 22.45, "change": 1.25, "change_percent": 5.89, "volume": 32000000}
        ]
        
        # 4. جلب الأخبار الاقتصادية (بيانات وهمية)
        data["news"] = [
            {"title": "البنك الفيدرالي يقرر الإبقاء على أسعار الفائدة دون تغيير", "source": "CNBC", "date": "2023-11-01", "impact": "عال"},
            {"title": "تقارير: نمو قوي في الوظائف غير الزراعية لشهر أكتوبر", "source": "Bloomberg", "date": "2023-11-03", "impact": "متوسط"},
            {"title": "انخفاض مفاجئ في مخزونات النفط الأمريكية", "source": "Reuters", "date": "2023-11-02", "impact": "عال"},
            {"title": "تقرير: تضخم أقل من المتوقع في منطقة اليورو", "source": "WSJ", "date": "2023-11-04", "impact": "متوسط"},
            {"title": "شركات التكنولوجيا الكبرى تعلن عن نتائج أرباح قوية", "source": "Financial Times", "date": "2023-11-05", "impact": "عال"}
        ]
        
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {str(e)}")
    
    return data

def display_market_indices(indices_data):
    """عرض المؤشرات الرئيسية"""
    st.header("📊 المؤشرات الرئيسية")
    
    if not indices_data:
        st.warning("لا تتوفر بيانات المؤشرات حالياً")
        return
    
    cols = st.columns(4)
    index_info = {
        "DJIA": {"name": "داو جونز", "emoji": "🏭"},
        "SPX": {"name": "S&P 500", "emoji": "📈"},
        "NDX": {"name": "ناسداك", "emoji": "💻"},
        "RUT": {"name": "راسل 2000", "emoji": "📊"}
    }
    
    for idx, (symbol, data) in enumerate(indices_data.items()):
        if data:
            change = float(data.get("05. price", 0)) - float(data.get("08. previous close", 0))
            change_percent = (change / float(data.get("08. previous close", 1))) * 100
            
            with cols[idx]:
                st.metric(
                    label=f"{index_info.get(symbol, {}).get('emoji', '📌')} {index_info.get(symbol, {}).get('name', symbol)}",
                    value=f"{float(data.get('05. price', 0)):,.2f}",
                    delta=f"{change_percent:.2f}%",
                    delta_color="normal"
                )

def display_stock_section(title, stocks, min_price=0.55):
    """عرض قسم الأسهم مع فلترة حسب السعر"""
    st.header(f"📌 {title}")
    
    # فلترة الأسهم حسب السعر
    filtered_stocks = [s for s in stocks if s["price"] >= min_price]
    
    if not filtered_stocks:
        st.warning(f"لا توجد أسهم تتجاوز قيمتها {min_price}$")
        return
    
    df = pd.DataFrame(filtered_stocks)
    df["change_color"] = df["change"].apply(lambda x: "green" if x >= 0 else "red")
    
    fig = go.Figure()
    
    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row["symbol"]],
            y=[abs(row["change_percent"])],
            name=row["name"],
            marker_color=row["change_color"],
            text=[f"{row['price']}$ ({row['change_percent']}%)"],
            textposition='auto'
        ))
    
    fig.update_layout(
        title=f"أداء {title} (تغير %)",
        yaxis_title="نسبة التغير %",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # عرض جدول تفصيلي
    st.dataframe(
        df[["symbol", "name", "price", "change", "change_percent", "volume"]]
        .rename(columns={
            "symbol": "الرمز",
            "name": "الشركة",
            "price": "السعر ($)",
            "change": "التغير ($)",
            "change_percent": "التغير %",
            "volume": "حجم التداول"
        }),
        height=300
    )

def display_economic_news(news_data):
    """عرض الأخبار الاقتصادية"""
    st.header("📰 الأخبار المؤثرة على الاقتصاد")
    
    if not news_data:
        st.warning("لا تتوفر أخبار حالياً")
        return
    
    for news in news_data:
        impact_color = {
            "عال": "red",
            "متوسط": "orange",
            "منخفض": "gray"
        }.get(news["impact"], "gray")
        
        with st.expander(f"{news['title']} - {news['source']} ({news['date']})"):
            st.markdown(f"**التأثير**: :{impact_color}[{news['impact']}]")
            st.write("هذا مثال لنص الخبر. في التطبيق الفعلي سيتم جلب النص الكامل من المصدر.")

# جلب وعرض البيانات
market_data = fetch_market_data()

if market_data:
    # 1. عرض المؤشرات الرئيسية
    display_market_indices(market_data["indices"])
    
    st.markdown("---")
    
    # 2. عرض الأسهم الأكثر ارتفاعاً (مع فلترة السعر)
    display_stock_section("الأسهم الأكثر ارتفاعاً", market_data["stocks"]["gainers"])
    
    st.markdown("---")
    
    # 3. عرض الأسهم الأكثر تداولاً (مع فلترة السعر)
    display_stock_section("الأسهم الأكثر تداولاً", market_data["stocks"]["most_active"])
    
    st.markdown("---")
    
    # 4. عرض الأخبار الاقتصادية
    display_economic_news(market_data["news"])

st.markdown("---")
st.markdown("""
**مصادر البيانات المقترحة:**
1. [Alpha Vantage](https://www.alphavantage.co/) - واجهة برمجة تطبيقات مجانية للبيانات المالية
2. [Financial Modeling Prep](https://financialmodelingprep.com/) - مصادر أخرى للبيانات المالية
3. [NewsAPI](https://newsapi.org/) - لجلب الأخبار الاقتصادية

**ملاحظات التطوير:**
1. للحصول على بيانات حقيقية، سجل في Alpha Vantage واحصل على مفتاح API مجاني
2. أضف المفتاح في إعدادات Streamlit (secrets.toml)
3. يمكن إضافة المزيد من المؤشرات والأسهم حسب الحاجة
""")
