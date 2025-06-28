import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
import os
#from dotenv import load_dotenv
#st.write("🔑 Alpha Vantage Key:", st.secrets.get("alpha_vantage", {}).get("api_key"))

st.set_page_config(page_title="نظرة على السوق الأمريكي", layout="wide")
st.title("📈 نظرة شاملة على السوق الأمريكي")

#st.write("المسار الحالي:", os.getcwd())
#st.write("محتويات مجلد .streamlit:", os.listdir(".streamlit"))

#load_dotenv('.env')  # تحديد المسار الصريح

#API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY") or "default_key_for_dev"

@st.cache_data(ttl=3600)
def fetch_market_data():
    try:
        if not hasattr(st, 'secrets') or not st.secrets.get("alpha_vantage", {}).get("api_key"):
            st.error("⚠️ إعدادات Alpha Vantage غير موجودة")
            st.info("""
            الرجاء التأكد من:
            1. وجود ملف `.streamlit/secrets.toml`
            2. احتوائه على قسم [alpha_vantage]
            3. وجود api_key داخل هذا القسم
            """)
            return get_sample_data()

        api_key = st.secrets["alpha_vantage"]["api_key"]
        indices_data = fetch_indices_data(api_key)
        gainers, losers, most_active = fetch_top_stocks(api_key)
        news_data = get_sample_news()

        return {
            "indices": indices_data,
            "stocks": {
                "gainers": gainers,
                "most_active": most_active
            },
            "news": news_data
        }

    except Exception as e:
        st.error(f"حدث خطأ في جلب البيانات: {str(e)}")
        return get_sample_data()

def fetch_indices_data(api_key):
    indices = {
        "DJIA": {"name": "داو جونز", "symbol": "^DJI", "emoji": "🏭"},
        "SPX": {"name": "S&P 500", "symbol": "^GSPC", "emoji": "📈"},
        "NDX": {"name": "ناسداك", "symbol": "^IXIC", "emoji": "💻"},
        "RUT": {"name": "راسل 2000", "symbol": "^RUT", "emoji": "📊"}
    }
    indices_data = {}
    for key, info in indices.items():
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={info['symbol']}&apikey={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                indices_data[key] = response.json().get("Global Quote", {})
        except:
            continue
    return indices_data

def fetch_top_stocks(api_key):
    try:
        url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
        response = requests.get(url)
        data = response.json()

        gainers = []
        losers = []
        most_active = []

        if "top_gainers" in data:
            for stock in data["top_gainers"][:5]:
                gainers.append({
                    "symbol": stock["ticker"],
                    "name": stock.get("companyName", stock["ticker"]),
                    "price": float(stock["price"]),
                    "change": float(stock["change_amount"]),
                    "change_percent": float(stock["change_percentage"].rstrip('%')),
                    "volume": int(stock["volume"])
                })

        if "most_actively_traded" in data:
            for stock in data["most_actively_traded"][:5]:
                most_active.append({
                    "symbol": stock["ticker"],
                    "name": stock.get("companyName", stock["ticker"]),
                    "price": float(stock["price"]),
                    "change": float(stock["change_amount"]),
                    "change_percent": float(stock["change_percentage"].rstrip('%')),
                    "volume": int(stock["volume"])
                })

        return gainers, losers, most_active

    except:
        return get_sample_stocks()

def get_sample_stocks():
    gainers = [
        {"symbol": "AAPL", "name": "Apple Inc", "price": 185.32, "change": 4.25, "change_percent": 2.35, "volume": 25000000},
        {"symbol": "TSLA", "name": "Tesla Inc", "price": 245.67, "change": 8.12, "change_percent": 3.42, "volume": 18000000},
        {"symbol": "NVDA", "name": "NVIDIA Corp", "price": 678.90, "change": 22.45, "change_percent": 3.42, "volume": 15000000}
    ]
    most_active = [
        {"symbol": "AAPL", "name": "Apple Inc", "price": 185.32, "change": 4.25, "change_percent": 2.35, "volume": 45000000},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "price": 165.78, "change": -2.45, "change_percent": -1.46, "volume": 42000000},
        {"symbol": "F", "name": "Ford Motor", "price": 12.45, "change": 0.25, "change_percent": 2.05, "volume": 38000000}
    ]
    return gainers, [], most_active

def get_sample_news():
    return [
        {"title": "البنك الفيدرالي يقرر الإبقاء على أسعار الفائدة دون تغيير", "source": "CNBC", "date": datetime.now().strftime("%Y-%m-%d"), "impact": "عال"},
        {"title": "تقارير: نمو قوي في الوظائف غير الزراعية", "source": "Bloomberg", "date": datetime.now().strftime("%Y-%m-%d"), "impact": "متوسط"}
    ]

def get_sample_data():
    return {
        "indices": {
            "DJIA": {"05. price": "34200.12", "08. previous close": "34025.45"},
            "SPX": {"05. price": "4380.34", "08. previous close": "4350.12"},
            "NDX": {"05. price": "14850.67", "08. previous close": "14780.23"}
        },
        "stocks": {
            "gainers": get_sample_stocks()[0],
            "most_active": get_sample_stocks()[2]
        },
        "news": get_sample_news()
    }

def display_market_indices(indices_data):
    st.header("📊 المؤشرات الرئيسية")
    if not indices_data:
        st.warning("لا تتوفر بيانات المؤشرات حالياً")
        return
    cols = st.columns(len(indices_data))
    index_info = {
        "DJIA": {"name": "داو جونز", "emoji": "🏭"},
        "SPX": {"name": "S&P 500", "emoji": "📈"},
        "NDX": {"name": "ناسداك", "emoji": "💻"},
        "RUT": {"name": "راسل 2000", "emoji": "📊"}
    }
    for idx, (symbol, data) in enumerate(indices_data.items()):
        if data:
            try:
                current_price = float(data.get("05. price", 0))
                prev_close = float(data.get("08. previous close", current_price))
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                with cols[idx]:
                    st.metric(
                        label=f"{index_info.get(symbol, {}).get('emoji', '📌')} {index_info.get(symbol, {}).get('name', symbol)}",
                        value=f"{current_price:,.2f}",
                        delta=f"{change_percent:.2f}%",
                        delta_color="normal"
                    )
            except:
                continue

def display_stock_section(title, stocks, min_price=0.55):
    st.header(f"📌 {title}")
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
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        df[["symbol", "name", "price", "change", "change_percent", "volume"]]
        .sort_values("change_percent", ascending=False)
        .rename(columns={
            "symbol": "الرمز",
            "name": "الشركة",
            "price": "السعر ($)",
            "change": "التغير ($)",
            "change_percent": "التغير %",
            "volume": "حجم التداول"
        }),
        height=300,
        use_container_width=True
    )

def display_economic_news(news_data):
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

def main():
    market_data = fetch_market_data()
    if market_data:
        display_market_indices(market_data["indices"])
        st.markdown("---")
        display_stock_section("الأسهم الأكثر ارتفاعاً", market_data["stocks"]["gainers"])
        st.markdown("---")
        display_stock_section("الأسهم الأكثر تداولاً", market_data["stocks"]["most_active"])
        st.markdown("---")
        display_economic_news(market_data["news"])

    st.markdown("---")
    st.markdown("""
    **مصادر البيانات المقترحة:**
    1. [Alpha Vantage](https://www.alphavantage.co/)
    2. [Financial Modeling Prep](https://financialmodelingprep.com/)
    3. [NewsAPI](https://newsapi.org/)

    **ملاحظات التطوير:**
    - للحصول على بيانات حقيقية، سجل في Alpha Vantage واحصل على مفتاح API مجاني
    - أضف المفتاح في إعدادات Streamlit (`.streamlit/secrets.toml`)
    """)

if __name__ == "__main__":
    main()
