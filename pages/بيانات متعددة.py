import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import time
import numpy as np
import requests
from io import StringIO

# --- إعدادات التطبيق ---
st.set_page_config(page_title="أداة الأسهم متعددة المصادر", layout="wide")
st.title('📈 أداة الأسهم الأكثر ارتفاعًا (متعددة المصادر)')

# --- إدارة مصادر البيانات ---
class DataSources:
    def __init__(self):
        self.sources = {
            "Yahoo Finance": {
                "name": "Yahoo Finance",
                "requires_key": False,
                "available": True
            },
            "Alpha Vantage": {
                "name": "Alpha Vantage",
                "requires_key": True,
                "available": False,
                "module": None
            },
            "Twelve Data": {
                "name": "Twelve Data",
                "requires_key": True,
                "available": False,
                "module": None
            },
            "Tiingo": {
                "name": "Tiingo",
                "requires_key": True,
                "available": False
            }
        }
        
        self._check_available_sources()
    
    def _check_available_sources(self):
        """فحص المصادر المتاحة"""
        # Alpha Vantage
        try:
            from alpha_vantage.timeseries import TimeSeries
            self.sources["Alpha Vantage"]["available"] = True
            self.sources["Alpha Vantage"]["module"] = TimeSeries
        except ImportError:
            pass
        
        # Twelve Data
        try:
            import twelvedata as td
            self.sources["Twelve Data"]["available"] = True
            self.sources["Twelve Data"]["module"] = td
        except ImportError:
            pass
        
        # Tiingo (لا يحتاج لمكتبة خاصة)
        self.sources["Tiingo"]["available"] = True
    
    def get_available_sources(self):
        """الحصول على قائمة المصادر المتاحة"""
        return [src for src in self.sources.values() if src["available"]]

# تهيئة مصادر البيانات
data_sources = DataSources()

# --- واجهة المستخدم ---
st.sidebar.header("إعدادات المصادر")

# اختيار مصدر البيانات
available_sources = [src["name"] for src in data_sources.get_available_sources()]
selected_source = st.sidebar.selectbox(
    "اختر مصدر البيانات:",
    available_sources,
    index=0
)

# إدخال مفاتيح API
api_keys = {}
for src in data_sources.get_available_sources():
    if src["requires_key"]:
        api_keys[src["name"]] = st.sidebar.text_input(
            f"مفتاح {src['name']} API:",
            type="password",
            key=f"{src['name']}_key"
        )

# --- وظائف جلب البيانات ---
def get_yfinance_data(symbol, period="1mo"):
    """جلب البيانات من Yahoo Finance"""
    try:
        data = yf.Ticker(symbol).history(period=period)
        time.sleep(0.5)  # تجنب حظر الطلبات
        return data[['Open', 'High', 'Low', 'Close', 'Volume']] if not data.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Yahoo Finance: {str(e)}")
        return pd.DataFrame()

def get_alphavantage_data(symbol, period="1mo"):
    """جلب البيانات من Alpha Vantage"""
    if not api_keys.get("Alpha Vantage"):
        st.error("الرجاء إدخال مفتاح Alpha Vantage API")
        return pd.DataFrame()
    
    try:
        ts = data_sources.sources["Alpha Vantage"]["module"](key=api_keys["Alpha Vantage"], output_format='pandas')
        data, _ = ts.get_daily(symbol=symbol, outputsize='full')
        data = data.sort_index()
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return data.last(period)
    except Exception as e:
        st.error(f"خطأ في Alpha Vantage: {str(e)}")
        return pd.DataFrame()

def get_twelvedata_data(symbol, period="1mo"):
    """جلب البيانات من Twelve Data"""
    if not api_keys.get("Twelve Data"):
        st.error("الرجاء إدخال مفتاح Twelve Data API")
        return pd.DataFrame()
    
    try:
        client = data_sources.sources["Twelve Data"]["module"].Client(apikey=api_keys["Twelve Data"])
        timeframe = "1day" if "mo" in period else "1hour"
        
        data = client.time_series(
            symbol=symbol,
            interval=timeframe,
            outputsize=100,
            timezone="UTC"
        ).as_pandas()
        
        if not data.empty:
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            return data.last(period)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Twelve Data: {str(e)}")
        return pd.DataFrame()

def get_tiingo_data(symbol, period="1mo"):
    """جلب البيانات من Tiingo"""
    if not api_keys.get("Tiingo"):
        st.error("الرجاء إدخال مفتاح Tiingo API")
        return pd.DataFrame()
    
    try:
        # حساب تاريخ البداية بناءً على الفترة المطلوبة
        end_date = datetime.now()
        if "mo" in period:
            months = int(period.replace("mo", ""))
            start_date = end_date - timedelta(days=months*30)
        else:
            days = int(period.replace("d", ""))
            start_date = end_date - timedelta(days=days)
        
        url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices?startDate={start_date.strftime('%Y-%m-%d')}&endDate={end_date.strftime('%Y-%m-%d')}&token={api_keys['Tiingo']}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = pd.read_json(StringIO(response.text))
        if not data.empty:
            data = data.set_index('date')
            data.index = pd.to_datetime(data.index)
            return data[['open', 'high', 'low', 'close', 'volume']].rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
        return pd.DataFrame()
    except Exception as e:
        st.error(f"خطأ في Tiingo: {str(e)}")
        return pd.DataFrame()

# --- الواجهة الرئيسية ---
tab1, tab2 = st.tabs(["الأسهم الصاعدة", "تحليل مفصل"])

with tab1:
    st.header("الأسهم الأكثر ارتفاعًا")
    
    market = st.selectbox("اختر السوق:", ["NASDAQ", "Tadawul", "S&P 500"])
    
    if st.button("جلب البيانات"):
        with st.spinner("جاري تحليل البيانات..."):
            if selected_source == "Yahoo Finance":
                if market == "NASDAQ":
                    symbols = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "TSLA", "NVDA"]
                elif market == "Tadawul":
                    symbols = ["2222.SR", "1180.SR", "7010.SR", "1211.SR", "2380.SR"]
                else:
                    symbols = ["SPY", "VOO", "IVV"]
                
                results = []
                for symbol in symbols:
                    data = get_yfinance_data(symbol)
                    if not data.empty and len(data) > 1:
                        change_pct = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                        results.append({
                            'السهم': symbol,
                            'السعر': data['Close'].iloc[-1],
                            'التغير %': change_pct,
                            'الحجم': data['Volume'].iloc[-1],
                            'المصدر': selected_source
                        })
                    time.sleep(0.5)  # تجنب حظر الطلبات
                
                if results:
                    df = pd.DataFrame(results).sort_values('التغير %', ascending=False)
                    st.dataframe(
                        df.style
                        .highlight_max(subset=['التغير %'], color='lightgreen')
                        .format({'السعر': "{:.2f}", 'التغير %': "{:.2f}%", 'الحجم': "{:,.0f}"}),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("لا توجد بيانات متاحة. حاول تغيير مصدر البيانات.")
            else:
                st.warning("حاليًا، دعم الأسواق متاح فقط مع Yahoo Finance")

with tab2:
    st.header("تحليل مفصل للسهم")
    symbol = st.text_input("ادخل رمز السهم:", "AAPL")
    
    if st.button("تحليل السهم"):
        if not symbol:
            st.warning("الرجاء إدخال رمز السهم")
        else:
            with st.spinner("جاري تحليل السهم..."):
                if selected_source == "Yahoo Finance":
                    data = get_yfinance_data(symbol, "3mo")
                elif selected_source == "Alpha Vantage":
                    data = get_alphavantage_data(symbol, "3mo")
                elif selected_source == "Twelve Data":
                    data = get_twelvedata_data(symbol, "3mo")
                elif selected_source == "Tiingo":
                    data = get_tiingo_data(symbol, "3mo")
                else:
                    data = pd.DataFrame()
                
                if not data.empty:
                    # التحليل
                    data['Daily_Return'] = data['Close'].pct_change() * 100
                    data['SMA_20'] = data['Close'].rolling(20).mean()
                    
                    # تحليل إضافي
                    data['Trend'] = np.where(data['Close'] > data['SMA_20'], 'صاعد', 'هابط')
                    average_volume = data['Volume'].rolling(window=20).mean()
                    data['Liquidity'] = np.where(data['Volume'] > average_volume, 'مرتفعة', 'منخفضة')
                
                    last_row = data.iloc[-1]
                    trend = last_row['Trend']
                    liquidity = last_row['Liquidity']
                    change_pct = last_row['Daily_Return']
                    price = last_row['Close']
                
                    analysis_text = f"""
                    📊 **تحليل تلقائي للسهم `{symbol}`:**
                
                    - 🔹 الاتجاه العام: **{trend}**
                    - 💧 السيولة: **{liquidity}**
                    - 📈 آخر سعر إغلاق: **{price:.2f}**
                    - 🔄 التغير اليومي: **{change_pct:.2f}%**
                    - 🧠 التقييم: {'فرصة شراء' if trend == 'صاعد' and liquidity == 'مرتفعة' else 'تحت المراقبة'}
                    """
                
                    # عرض المقاييس
                    col1, col2 = st.columns(2)
                    col1.metric("آخر سعر", f"{price:.2f}")
                    col1.metric("التغير اليومي", f"{change_pct:.2f}%")
                    col2.metric("حجم التداول", f"{last_row['Volume']:,.0f}")
                    col2.metric("المتوسط المتحرك", f"{last_row['SMA_20']:.2f}")
                
                    # الشارتات
                    fig1 = px.line(data, x=data.index, y=['Close', 'SMA_20'], 
                                   title=f"أداء السهم {symbol} (مصدر: {selected_source})")
                    st.plotly_chart(fig1, use_container_width=True)
                
                    fig2 = px.bar(data, x=data.index, y='Volume',
                                 title=f"حجم التداول لـ {symbol}")
                    st.plotly_chart(fig2, use_container_width=True)
                
                    # عرض التحليل النصي
                    st.markdown(analysis_text)
                else:
                    st.error("فشل في جلب البيانات. حاول:")
                    st.markdown("""
                    1. التأكد من صحة رمز السهم  
                    2. التحقق من مفتاح API  
                    3. تجربة مصدر بيانات مختلف
                    """)

    
                    # عرض النتائج
                    col1, col2 = st.columns(2)
                    col1.metric("آخر سعر", f"{data['Close'].iloc[-1]:.2f}")
                    col1.metric("التغير اليومي", f"{data['Daily_Return'].iloc[-1]:.2f}%")
                    col2.metric("حجم التداول", f"{data['Volume'].iloc[-1]:,.0f}")
                    col2.metric("المتوسط المتحرك", f"{data['SMA_20'].iloc[-1]:.2f}")
                    
                    # الرسوم البيانية
                    fig1 = px.line(data, x=data.index, y=['Close', 'SMA_20'], 
                                 title=f"أداء السهم {symbol} (مصدر: {selected_source})")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    fig2 = px.bar(data, x=data.index, y='Volume',
                                 title=f"حجم التداول لـ {symbol}")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.error("فشل في جلب البيانات. حاول:")
                    st.markdown("""
                    1. التأكد من صحة رمز السهم
                    2. التحقق من مفتاح API
                    3. تجربة مصدر بيانات مختلف
                    """)
                    st.markdown(analysis_text)
# --- تذييل الصفحة ---
st.markdown("""
---
**ملاحظات مهمة:**
1. Yahoo Finance لا يحتاج لمفتاح API
2. Tiingo وAlpha Vantage وTwelve Data تحتاج مفاتيح API صالحة
3. بعض المصادر قد يكون لديها قيود على عدد الطلبات
4. الأسعار قد تكون متأخرة حسب المصدر
""")

