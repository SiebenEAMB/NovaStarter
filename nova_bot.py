# NovaBot v2 - Webhook Mode (Sieben Edition)
# Features: Telegram + Groq + OpenRouter + Flask Webhook

import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nova")

# Init Flask app
app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

# Start command
def start(update, context):
    update.message.reply_text("Sieben, the world is yours. Superbrain webhook is live.")

# Handle messages
def handle_message(update, context):
    user_message = update.message.text
    user_id = update.message.from_user.id
    logger.info(f"Message from {user_id}: {user_message}")
    response = query_llms(user_message)
    update.message.reply_text(response)

# --- LLM LOGIC ---
def query_llms(prompt):
    try:
        return query_openrouter(prompt)
    except Exception as e:
        logger.warning(f"OpenRouter failed: {e}")
        try:
            return query_groq(prompt)
        except Exception as e:
            logger.error(f"Groq failed: {e}")
            return "Nova failed to think."

# --- OPENROUTER ---
def query_openrouter(prompt):
    key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openrouter/openchat-3.5",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "stream": False
    }
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

# --- GROQ ---
def query_groq(prompt):
    key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "stream": False
    }
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

# --- Routes ---
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# --- Webhook Setup ---
@app.route("/")
def index():
    webhook_url = os.getenv("WEBHOOK_URL")
    bot.set_webhook(f"{webhook_url}/{TOKEN}")
    return "Nova webhook is set."

# --- Register Handlers ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Run Flask app ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
