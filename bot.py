import telebot
import os
import google.generativeai as genai

# ==================== توکن‌ها ====================
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)

# تنظیم Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ذخیره تاریخچه چت هر کاربر
chat_sessions = {}

# ==================== شروع ====================

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    text = f"""
👋 سلام {name} عزیز!

من یه دستیار هوش مصنوعی هستم 🤖
هر سوالی داری بپرس، اینجام 😊

/clear - پاک کردن تاریخچه مکالمه
"""
    bot.send_message(message.chat.id, text)

# ==================== پاک کردن تاریخچه ====================

@bot.message_handler(commands=['clear'])
def clear_history(message):
    user_id = message.from_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    bot.send_message(message.chat.id, "✅ تاریخچه پاک شد! دوباره شروع کن.")

# ==================== دریافت پیام و پاسخ AI ====================

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id

    try:
        bot.send_chat_action(message.chat.id, 'typing')

        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])

        chat = chat_sessions[user_id]
        response = chat.send_message(message.text)

        bot.send_message(message.chat.id, response.text)

    except Exception as e:
        bot.send_message(message.chat.id, "❌ خطایی رخ داد! دوباره امتحان کن یا /start بزن.")

# ==================== اجرا ====================

print("✅ ربات شروع به کار کرد...")
bot.infinity_polling()
