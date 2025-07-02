from ta.volume import OnBalanceVolumeIndicator
from ta.momentum import RSIIndicator  # MFI مشتق من RSI مع حجم التداول
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(stock_data['Close'], label='السعر')
plt.scatter(filtered_stocks.index, filtered_stocks['Close'], color='green', label='إشارات شراء')
plt.legend()
plt.show()
# حساب OBV
obv_indicator = OnBalanceVolumeIndicator(close=stock_data['Close'], volume=stock_data['Volume'])
stock_data['OBV'] = obv_indicator.on_balance_volume()

# حساب MFI (Money Flow Index)
# ملاحظة: مكتبة `ta` لا تحتوي على MFI مباشرة، لذا نستخدم العملية الحسابية يدويًا:
def calculate_mfi(data, window=14):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    money_flow = typical_price * data['Volume']
    
    positive_flow = []
    negative_flow = []
    
    for i in range(1, len(typical_price)):
        if typical_price[i] > typical_price[i-1]:
            positive_flow.append(money_flow[i-1])
            negative_flow.append(0)
        elif typical_price[i] < typical_price[i-1]:
            negative_flow.append(money_flow[i-1])
            positive_flow.append(0)
        else:
            positive_flow.append(0)
            negative_flow.append(0)
    
    positive_mf = pd.Series(positive_flow).rolling(window).sum()
    negative_mf = pd.Series(negative_flow).rolling(window).sum()
    
    mfi = 100 - (100 / (1 + (positive_mf / negative_mf)))
    return mfi

stock_data['MFI'] = calculate_mfi(stock_data)
