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

# تنظیم Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# ذخیره تاریخچه چت
chat_sessions = {}

# ==================== شروع ====================

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f"👋 سلام {name}!\n\nمن دستیار هوش مصنوعی هستم 🤖\nهر سوالی داری بپرس!\n\n/clear - پاک کردن تاریخچه")

@bot.message_handler(commands=['clear'])
def clear_history(message):
    chat_sessions[message.from_user.id] = []
    bot.send_message(message.chat.id, "✅ تاریخچه پاک شد!")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []

        chat_sessions[user_id].append({
            "role": "user",
            "parts": [{"text": message.text}]
        })

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=chat_sessions[user_id]
        )
        reply = response.text

        chat_sessions[user_id].append({
            "role": "model",
            "parts": [{"text": reply}]
        })

        bot.send_message(message.chat.id, reply)

    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(message.chat.id, f"❌ خطا: {str(e)[:100]}")

# ==================== Routes ====================

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return "OK", 200

# Health check برای Leapcell
@app.route("/", methods=['GET'])
@app.route("/kaithhealthcheck", methods=['GET'])
@app.route("/health", methods=['GET'])
def health():
    return "OK", 200

# ==================== اجرا ====================

bot.remove_webhook()
bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
print(f"✅ Webhook set: {WEBHOOK_URL}/{TOKEN}")
