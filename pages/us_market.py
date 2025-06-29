mport streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
import os

def main():
    st.title("📊 لوحة تحليل السوق الأمريكي - بيانات حقيقية")
    
    # التحقق من وجود API Key
    if "alpha_vantage" not in st.secrets:
        st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
        st.stop()
    
    api_key = st.secrets["alpha_vantage"]["api_key"]
    
    @st.cache_data(ttl=3600)
    def fetch_real_time_data():
        try:
            # جلب بيانات الأسهم والمؤشرات الحقيقية
            endpoints = {
                "market_status": f"https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={api_key}",
                "gainers_losers": f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}",
                "sp500": f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=^GSPC&apikey={api_key}",
                "dow_jones": f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=^DJI&apikey={api_key}",
                "nasdaq": f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=^IXIC&apikey={api_key}"
            }
            
            responses = {}
            for name, url in endpoints.items():
                response = requests.get(url)
                if response.status_code == 200:
                    responses[name] = response.json()
                else:
                    st.warning(f"فشل جلب بيانات {name.replace('_', ' ')}")
            
            return responses
        
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {str(e)}")
            return None
    
    data = fetch_real_time_data()
    
    if not data:
        st.error("❌ تعذر جلب البيانات من السوق. يرجى التحقق من اتصال الإنترنت أو مفتاح API")
        st.stop()
    
    # عرض حالة السوق (مع التحقق من وجود الأعمدة)
    if "market_status" in data and "markets" in data["market_status"]:
        st.header("🔄 حالة السوق الحالية")
        market_status = data["market_status"]["markets"]
        
        if market_status and isinstance(market_status, list):
            try:
                status_df = pd.DataFrame(market_status)
                
                # التحقق من وجود الأعمدة المطلوبة
                available_columns = status_df.columns.tolist()
                required_columns = ["market_type", "region", "current_status", "last_updated"]
                columns_to_show = [col for col in required_columns if col in available_columns]
                
                if columns_to_show:
                    st.dataframe(status_df[columns_to_show].rename(columns={
                        "market_type": "نوع السوق",
                        "region": "المنطقة",
                        "current_status": "الحالة",
                        "last_updated": "آخر تحديث"
                    }))
                else:
                    st.warning("بيانات حالة السوق لا تحتوي على الأعمدة المطلوبة")
                    st.write("الأعمدة المتاحة:", available_columns)
            except Exception as e:
                st.error(f"خطأ في معالجة بيانات حالة السوق: {str(e)}")
   #-----------------------------666666666666666666666--------------------------------------------- 
    data = fetch_real_time_data()
    
    if not data:
        st.error("❌ تعذر جلب البيانات من السوق. يرجى التحقق من اتصال الإنترنت أو مفتاح API")
        st.stop()
    
    # عرض حالة السوق
    if "market_status" in data:
        st.header("🔄 حالة السوق الحالية")
        market_status = data["market_status"].get("markets", [])
        if market_status:
            status_df = pd.DataFrame(market_status)
            st.dataframe(status_df[["market_type", "region", "current_status", "last_updated"]]
                        .rename(columns={
                            "market_type": "نوع السوق",
                            "region": "المنطقة",
                            "current_status": "الحالة",
                            "last_updated": "آخر تحديث"
                        }))
    
    # عرض المؤشرات الرئيسية
    st.header("📌 المؤشرات الرئيسية")
    cols = st.columns(3)
    
    indices = {
        "sp500": {"name": "S&P 500", "symbol": "^GSPC"},
        "dow_jones": {"name": "Dow Jones", "symbol": "^DJI"},
        "nasdaq": {"name": "NASDAQ", "symbol": "^IXIC"}
    }
    
    for idx, (key, info) in enumerate(indices.items()):
        if key in data and "Global Quote" in data[key]:
            quote = data[key]["Global Quote"]
            with cols[idx]:
                st.metric(
                    info["name"],
                    f"{float(quote.get('05. price', 0)):,.2f}",
                    delta=f"{float(quote.get('10. change percent', '0').replace('%','')):.2f}%"
                )
    
    # عرض الأسهم الأكثر ارتفاعاً
    if "gainers_losers" in data:
        st.header("🚀 الأسهم الأكثر ارتفاعاً")
        gainers = data["gainers_losers"].get("top_gainers", [])
        if gainers:
            gainers_df = pd.DataFrame(gainers)
            
            # تحويل الأنواع
            gainers_df["change_percentage"] = gainers_df["change_percentage"].str.replace('%', '').astype(float)
            gainers_df["price"] = gainers_df["price"].astype(float)
            
            # عرض الجدول
            st.dataframe(gainers_df[["ticker", "price", "change_amount", "change_percentage", "volume"]]
                .rename(columns={
                    "ticker": "الرمز",
                    "price": "السعر ($)",
                    "change_amount": "التغير ($)",
                    "change_percentage": "التغير %",
                    "volume": "الحجم"
                }))
            
            # رسم بياني
            fig = go.Figure(go.Bar(
                x=gainers_df["ticker"],
                y=gainers_df["change_percentage"],
                text=gainers_df["change_percentage"].round(2).astype(str) + '%',
                marker_color='green'
            ))
            fig.update_layout(
                title="أعلى 5 أسهم في الصعود",
                yaxis_title="نسبة الصعود %",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # قسم التحليل الفني (باستخدام بيانات حقيقية)
    st.header("📈 التحليل الفني")
    if "gainers_losers" in data and "most_actively_traded" in data["gainers_losers"]:
        active_stocks = [stock["ticker"] for stock in data["gainers_losers"]["most_actively_traded"][:5]]
        selected_stock = st.selectbox("اختر سهم للتحليل", active_stocks)
        
        if st.button("عرض البيانات التاريخية"):
            try:
                hist_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={selected_stock}&apikey={api_key}&outputsize=compact"
                hist_data = requests.get(hist_url).json()
                
                if "Time Series (Daily)" in hist_data:
                    df = pd.DataFrame(hist_data["Time Series (Daily)"]).T
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)
                    
                    st.line_chart(df["4. close"])
                else:
                    st.warning("لا توجد بيانات تاريخية متاحة")
            except Exception as e:
                st.error(f"خطأ في جلب البيانات التاريخية: {str(e)}")

if __name__ == "__main__":
    main()
