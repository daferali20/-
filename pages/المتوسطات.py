import streamlit as st
import pandas as pd
import talib  # بديل عن pandas_ta

# عنوان التطبيق
st.title("🚀 تحليل التداول باستخدام المتوسطات المتحركة")

# تحميل بيانات مثاليه
data = pd.DataFrame({
    'close': [3300, 3310, 3320, 3330, 3340, 3350, 3360, 3355, 3345, 3335]
})

# حساب المتوسطات باستخدام TA-Lib
data['MA_50'] = talib.SMA(data['close'], timeperiod=50)
data['MA_100'] = talib.SMA(data['close'], timeperiod=100)

# عرض البيانات
st.write("### بيانات الأسعار والمتوسطات المتحركة")
st.dataframe(data)

# رسم بياني
st.line_chart(data[['close', 'MA_50', 'MA_100']])
