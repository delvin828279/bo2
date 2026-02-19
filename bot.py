import os
import telebot
from google import genai
from flask import Flask, request

# ==================== توکن‌ها ====================
TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# تنظیم Gemini جدید
client = genai.Client(api_key=GEMINI_API_KEY)

# ذخیره تاریخچه چت
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
    chat_sessions[user_id] = []
    bot.send_message(message.chat.id, "✅ تاریخچه پاک شد!")

# ==================== پیام‌ها ====================

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    try:
        bot.send_chat_action(message.chat.id, 'typing')

        if user_id not in chat_sessions:
            chat_sessions[user_id] = []

        # اضافه کردن پیام کاربر به تاریخچه
        chat_sessions[user_id].append({
            "role": "user",
            "parts": [{"text": message.text}]
        })

        # ارسال به Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=chat_sessions[user_id]
        )

        reply = response.text

        # اضافه کردن جواب به تاریخچه
        chat_sessions[user_id].append({
            "role": "model",
            "parts": [{"text": reply}]
        })

        bot.send_message(message.chat.id, reply)

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, "❌ خطایی رخ داد! دوباره امتحان کن.")

# ==================== Webhook ====================

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=['GET'])
def index():
    return "✅ ربات آنلاینه!", 200

# ==================== اجرا ====================

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    print(f"✅ Webhook set!")
    app.run(host="0.0.0.0", port=8080)
