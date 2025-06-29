import requests

token = "توكن البوت"
chat_id = "@اسم_القناة"
message = "📢 اختبار إرسال من بايثون إلى تليجرام"

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": message,
    "parse_mode": "HTML"
}

response = requests.post(url, data=payload)
print(response.status_code)
print(response.text)
