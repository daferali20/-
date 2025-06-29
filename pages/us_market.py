import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# ✅ الدالة الرئيسية التي تنفذ الواجهة
def main():
    st.title("📊 لوحة تحليل السوق الأمريكي - بيانات حقيقية")

    # ✅ تحقق من توفر مفتاح Alpha Vantage في secrets
    if "alpha_vantage" not in st.secrets:
        st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
        st.stop()
    
    api_key = st.secrets["alpha_vantage"]["api_key"]

    # ✅ دالة جلب بيانات من API (تُخزن مؤقتًا لمدة ساعة)
    @st.cache_data(ttl=3600)
    def fetch_real_time_data():
        try:
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
            st.error(f"❌ خطأ في جلب البيانات: {str(e)}")
            return None

    # ✅ جلب البيانات
    data = fetch_real_time_data()

    if not data:
        st.error("❌ تعذر جلب البيانات من السوق.")
        st.stop()

    # ✅ عرض حالة السوق
    if "market_status" in data:
        st.header("🔄 حالة السوق الحالية")
        market_status = data["market_status"].get("markets", [])
        if market_status:
            status_df = pd.DataFrame(market_status)
            expected_cols = ["market_type", "region", "current_status", "last_updated"]
            available_cols = status_df.columns.tolist()

            if all(col in available_cols for col in expected_cols):
                st.dataframe(
                    status_df[expected_cols].rename(columns={
                        "market_type": "نوع السوق",
                        "region": "المنطقة",
                        "current_status": "الحالة",
                        "last_updated": "آخر تحديث"
                    })
                )
            else:
                st.warning("⚠️ تنسيق بيانات حالة السوق غير متوقع.")
                st.write(status_df)
        else:
            st.info("لا توجد بيانات لحالة السوق حالياً.")

    # ✅ عرض المؤشرات الرئيسية (S&P 500, Dow Jones, Nasdaq)
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
            price = float(quote.get("05. price", 0))
            change_percent = float(quote.get("10. change percent", "0").replace('%',''))
            with cols[idx]:
                st.metric(info["name"], f"{price:,.2f}", f"{change_percent:.2f}%")

    # ✅ عرض الأسهم الأكثر ارتفاعًا
    if "gainers_losers" in data:
        st.header("🚀 الأسهم الأكثر ارتفاعاً")
        gainers = data["gainers_losers"].get("top_gainers", [])
        if gainers:
            gainers_df = pd.DataFrame(gainers)
            try:
                gainers_df["change_percentage"] = gainers_df["change_percentage"].str.replace('%', '').astype(float)
                gainers_df["price"] = gainers_df["price"].astype(float)
                st.dataframe(
                    gainers_df[["ticker", "price", "change_amount", "change_percentage", "volume"]].rename(columns={
                        "ticker": "الرمز",
                        "price": "السعر ($)",
                        "change_amount": "التغير ($)",
                        "change_percentage": "التغير %",
                        "volume": "الحجم"
                    })
                )
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
            except Exception as e:
                st.error(f"⚠️ تعذر معالجة بيانات الأسهم المرتفعة: {str(e)}")

    # ✅ التحليل الفني - اختيار سهم وتحليل بياناته التاريخية
    st.header("📈 التحليل الفني")
    if "gainers_losers" in data and "top_gainers" in data["gainers_losers"]:
        active_stocks = [stock["ticker"] for stock in data["gainers_losers"]["top_gainers"][:5]]
        selected_stock = st.selectbox("اختر سهم للتحليل", active_stocks)
        if st.button("عرض البيانات التاريخية"):
            try:
                hist_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={selected_stock}&apikey={api_key}&outputsize=compact"
                hist_data = requests.get(hist_url).json()
                if "Time Series (Daily)" in hist_data:
                    df = pd.DataFrame(hist_data["Time Series (Daily)"]).T
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df["4. close"],
                        mode='lines',
                        name='سعر الإغلاق'
                    ))
                    fig.update_layout(
                        title=f"سعر سهم {selected_stock} التاريخي",
                        xaxis_title="التاريخ",
                        yaxis_title="السعر ($)",
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("لا توجد بيانات تاريخية متاحة للسهم المختار.")
            except Exception as e:
                st.error(f"❌ خطأ في جلب البيانات التاريخية: {str(e)}")

# ✅ إعداد الصفحة وتشغيل التطبيق
if __name__ == "__main__":
    st.set_page_config(
        page_title="لوحة تحليل السوق الأمريكي",
        page_icon="📊",
        layout="wide"
    )
    main()
