# NovaBot - PTB 13.15 Webhook Edition
import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from datetime import datetime

# Init logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nova")

# Init Flask app
app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=4)

# Commands
def start(update, context):
    update.message.reply_text("Sieben, the world is yours. Nova is live.")

def handle_message(update, context):
    text = update.message.text
    logger.info(f"User: {update.message.from_user.id} said: {text}")
    reply = query_llms(text)
    update.message.reply_text(reply)

# LLM brain
def query_llms(prompt):
    try:
        return query_openrouter(prompt)
    except Exception as e:
        logger.warning(f"OpenRouter fail: {e}")
        try:
            return query_groq(prompt)
        except Exception as e:
            logger.error(f"Groq fail: {e}")
            return "Nova failed to respond."

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
    return r.json()["choices"][0]["message"]["content"]

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
    return r.json()["choices"][0]["message"]["content"]

# Flask routes
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def set_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    bot.set_webhook(f"{webhook_url}/{TOKEN}")
    return "Webhook set"

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
