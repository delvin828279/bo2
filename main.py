import os
import telebot
import google.generativeai as genai
from flask import Flask
import threading

# دریافت کلیدها از متغیرهای محیطی سیستم (برای امنیت بیشتر)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تنظیمات اتصال به هوش مصنوعی جمنای
genai.configure(api_key=GEMINI_API_KEY)
# استفاده از مدل جدید و سریع جمنای
model = genai.GenerativeModel('gemini-1.5-flash')

# راه‌اندازی ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# پاسخ به دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! من یک هوش مصنوعی متصل به Gemini هستم. هر سوالی داری ازم بپرس! 🤖")

# دریافت متن‌های کاربر و ارسال به جمنای
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    try:
        # نمایش حالت "در حال تایپ..." در تلگرام کاربر
        bot.send_chat_action(message.chat.id, 'typing')
        
        # ارسال پیام کاربر به جمنای و دریافت جواب
        response = model.generate_content(message.text)
        
        # ارسال جواب جمنای به کاربر در تلگرام
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, f"متاسفانه خطایی رخ داد. لطفا دوباره تلاش کن.\n{str(e)}")

# ==========================================
# تنظیمات سرور وب (Flask) برای اجرای بدون مشکل در Leapcell
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "ربات تلگرام با موفقیت در حال اجراست!"

def run_bot():
    # اجرای مداوم ربات تلگرام
    bot.infinity_polling()

if __name__ == "__main__":
    # اجرای ربات تلگرام در پس‌زمینه (Thread جداگانه)
    threading.Thread(target=run_bot, daemon=True).start()
    
    # اجرای سرور وب برای پاس کردن تست‌های سلامتی (Health check) سایت Leapcell
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
