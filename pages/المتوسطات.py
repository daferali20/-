import yfinance as yf
import pandas_ta as ta
import pandas as pd

# تحميل بيانات سهم أبل لمدة سنة يوميًا
ticker = 'AAPL'
data = yf.download(ticker, period='1y', interval='1d')

# إعادة تسمية الأعمدة لتتوافق مع pandas_ta
data.rename(columns={'Close': 'close', 'High': 'high', 'Low': 'low'}, inplace=True)

# حساب المتوسطات المتحركة
data['MA_50'] = ta.sma(data['close'], length=50)
data['MA_100'] = ta.sma(data['close'], length=100)
data['MA_200'] = ta.sma(data['close'], length=200)
data['MA_360'] = ta.sma(data['close'], length=360)

# دالة توليد إشارات التداول
def generate_signals(data):
    signals = []
    for i in range(1, len(data)):
        for ma in ['MA_50', 'MA_100', 'MA_200', 'MA_360']:
            if pd.isna(data[ma].iloc[i-1]):
                continue
            if data['low'].iloc[i-1] <= data[ma].iloc[i-1] <= data['high'].iloc[i-1]:
                if data['close'].iloc[i-1] > data[ma].iloc[i-1]:
                    signals.append(('BUY', data.index[i], ma))
                elif data['close'].iloc[i-1] < data[ma].iloc[i-1]:
                    signals.append(('SELL', data.index[i], ma))
    return signals

# حساب الإشارات
signals = generate_signals(data)
print(f"📊 إشارات التداول لسهم {ticker}:")
for signal in signals[-10:]:  # عرض آخر 10 إشارات
    print(signal)
