import pandas as pd
import pandas_ta as ta
import numpy as np

# مثال على بيانات أسعار (يتم استبدالها ببيانات حية من API)
data = pd.DataFrame({
    'close': [3300, 3310, 3320, 3330, 3340, 3350, 3360, 3355, 3345, 3335],
    'high': [3310, 3320, 3330, 3340, 3350, 3360, 3370, 3360, 3350, 3340],
    'low': [3290, 3300, 3310, 3320, 3330, 3340, 3350, 3340, 3330, 3320]
})

# حساب المتوسطات المتحركة
data['MA_50'] = ta.sma(data['close'], length=50)
data['MA_100'] = ta.sma(data['close'], length=100)
data['MA_200'] = ta.sma(data['close'], length=200)
data['MA_360'] = ta.sma(data['close'], length=360)

# تحديد إشارات الدخول
def generate_signals(data):
    signals = []
    for i in range(1, len(data)):
        # الشرط: السعر يلمس المتوسط ويغلق فوقه/تحته
        for ma in ['MA_50', 'MA_100', 'MA_200', 'MA_360']:
            if (data['low'].iloc[i-1] <= data[ma].iloc[i-1] <= data['high'].iloc[i-1]):
                if data['close'].iloc[i-1] > data[ma].iloc[i-1]:
                    signals.append(('BUY', data.index[i], ma))  # الدخول عند فتح الشمعة التالية
                elif data['close'].iloc[i-1] < data[ma].iloc[i-1]:
                    signals.append(('SELL', data.index[i], ma))
    return signals

signals = generate_signals(data)
print("إشارات التداول:", signals)
