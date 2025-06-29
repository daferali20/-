import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

def main():
    st.title("📊 تحليل سوق الأسهم الأمريكية - مباشر")

    # ✅ التحقق من وجود مفتاح Alpha Vantage
    if "alpha_vantage" not in st.secrets:
        st.error("⚠️ إعدادات Alpha Vantage غير موجودة في secrets.toml")
        st.stop()
    
    api_key = st.secrets["alpha_vantage"]["api_key"]

    # ✅ دالة جلب البيانات من Alpha Vantage
    @st.cache_data(ttl=3600)
    def fetch_market_data():
        try:
            url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {str(e)}")
            return None

    # ✅ جلب البيانات
    data = fetch_market_data()

    if not data:
        st.error("❌ تعذر جلب البيانات. تحقق من الاتصال أو API.")
        st.stop()

    # ✅ عرض الأسهم الأمريكية الأكثر ارتفاعًا
    st.header("🚀 الأسهم الأمريكية الأكثر ارتفاعاً اليوم")
    gainers = data.get("top_gainers", [])
    if gainers:
        try:
            gainers_df = pd.DataFrame(gainers)
            gainers_df["change_percentage"] = gainers_df["change_percentage"].str.replace('%', '').astype(float)
            gainers_df["price"] = gainers_df["price"].astype(float)

            # ✅ عرض جدول الأسهم
            st.dataframe(
                gainers_df[["ticker", "price", "change_amount", "change_percentage", "volume"]].rename(columns={
                    "ticker": "الرمز",
                    "price": "السعر ($)",
                    "change_amount": "التغير ($)",
                    "change_percentage": "النسبة %",
                    "volume": "الحجم"
                })
            )

            # ✅ رسم بياني لأعلى 5 أسهم صعودًا
            fig = go.Figure(go.Bar(
                x=gainers_df["ticker"].head(5),
                y=gainers_df["change_percentage"].head(5),
                text=gainers_df["change_percentage"].head(5).round(2).astype(str) + '%',
                marker_color='green'
            ))
            fig.update_layout(
                title="أعلى 5 أسهم أمريكية في الصعود",
                yaxis_title="نسبة الصعود %",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ خطأ في معالجة بيانات الأسهم: {str(e)}")
    else:
        st.info("لا توجد بيانات حالياً.")

    # ✅ التحليل الفني لسهم أمريكي مختار
    st.header("📈 التحليل الفني للسهم")
    if "top_gainers" in data:
        stocks = [item["ticker"] for item in data["top_gainers"][:5]]
        selected = st.selectbox("اختر السهم:", stocks)

        if st.button("عرض الرسم البياني التاريخي"):
            try:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={selected}&apikey={api_key}&outputsize=compact"
                res = requests.get(url).json()

                if "Time Series (Daily)" in res:
                    df = pd.DataFrame(res["Time Series (Daily)"]).T
                    df.index = pd.to_datetime(df.index)
                    df = df.astype(float)

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df["4. close"], mode='lines', name="سعر الإغلاق"))
                    fig.update_layout(
                        title=f"📉 التاريخ السعري لسهم {selected}",
                        xaxis_title="التاريخ",
                        yaxis_title="السعر ($)",
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("لا توجد بيانات تاريخية متاحة.")
            except Exception as e:
                st.error(f"❌ فشل في تحميل البيانات التاريخية: {str(e)}")

# ✅ إعداد صفحة Streamlit وتشغيل الواجهة
if __name__ == "__main__":
    st.set_page_config(
        page_title="سوق الأسهم الأمريكية",
        page_icon="📊",
        layout="wide"
    )
    main()
