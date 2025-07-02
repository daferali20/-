import pandas as pd
import pandas_ta as ta

# بيانات بسيطة
df = pd.DataFrame({
    "close": [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10]
})

# حساب RSI
df['RSI'] = ta.rsi(df['close'])

print(df)
