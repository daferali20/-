# us_market.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import os

# إعدادات الصفحة
st.set_page_config(page_title="نظرة على السوق الأمريكي", layout="wide")
st.title("📈 نظرة شاملة على السوق الأمريكي")

def main():
    @st.cache_data(ttl=3600)
    def fetch_market_data():
        """جلب بيانات السوق من Alpha Vantage مع معالجة الأخطاء"""
        try:
            # التحقق من وجود المفتاح
            if "alpha_vantage" not in st.secrets:
                st.error("إعدادات Alpha Vantage غير موجودة في ملف secrets.toml")
                return get_sample_data()
            
            api_key = st.secrets["alpha_vantage"]["api_key"]
            
            # إذا كان المفتاح غير صالح، استخدم بيانات وهمية
            if not api_key or api_key == "your_api_key_here":
                st.warning("يتم استخدام بيانات تجريبية لأن مفتاح API غير صالح")
                return get_sample_data()
            
            # جلب بيانات المؤشرات الرئيسية
            indices_data = fetch_indices_data(api_key)
            
            # جلب الأسهم الأكثر نشاطاً (حقيقية)
            gainers, losers, most_active = fetch_top_stocks(api_key)
            
            # جلب الأخبار الاقتصادية (بيانات وهمية في هذا المثال)
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
        """جلب بيانات المؤشرات الرئيسية"""
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
        """جلب الأسهم الأكثر نشاطاً"""
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
            # إذا فشل جلب البيانات الحقيقية، نستخدم بيانات وهمية
            return get_sample_stocks()

    def get_sample_stocks():
        """إرجاع بيانات أسهم وهمية"""
        gainers = [
            {"symbol": "AAPL", "name": "Apple Inc", "price": 185.32, "change": 4.25, 
             "change_percent": 2.35, "volume": 25000000},
            {"symbol": "TSLA", "name": "Tesla Inc", "price": 245.67, "change": 8.12, 
             "change_percent": 3.42, "volume": 18000000},
            {"symbol": "NVDA", "name": "NVIDIA Corp", "price": 678.90, "change": 22.45, 
             "change_percent": 3.42, "volume": 15000000}
        ]
        
        most_active = [
            {"symbol": "AAPL", "name": "Apple Inc", "price": 185.32, "change": 4.25, 
             "change_percent": 2.35, "volume": 45000000},
            {"symbol": "AMD", "name": "Advanced Micro Devices", "price": 165.78, 
             "change": -2.45, "change_percent": -1.46, "volume": 42000000},
            {"symbol": "F", "name": "Ford Motor", "price": 12.45, "change": 0.25, 
             "change_percent": 2.05, "volume": 38000000}
        ]
        
        return gainers, [], most_active

    def get_sample_news():
        """إرجاع أخبار وهمية"""
        return [
            {"title": "البنك الفيدرالي يقرر الإبقاء على أسعار الفائدة دون تغيير", 
             "source": "CNBC", "date": datetime.now().strftime("%Y-%m-%d"), "impact": "عال"},
            {"title": "تقارير: نمو قوي في الوظائف غير الزراعية", 
             "source": "Bloomberg", "date": datetime.now().strftime("%Y-%m-%d"), "impact": "متوسط"}
        ]

    def get_sample_data():
        """إرجاع بيانات وهمية كاملة"""
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
        """عرض المؤشرات الرئيسية"""
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
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # عرض جدول تفصيلي
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

if __name__ == "__main__":
    main()
