import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import logging

# --- Setup Logging ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Init Flask ---
app = Flask(__name__)

# --- Telegram Bot Setup ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
print(f"Setting webhook to: {WEBHOOK_URL}")  # Debug log to confirm URL

bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# --- Handlers ---
def start(update, context):
    update.message.reply_text("Nova online. How can I assist you today?")

def handle_message(update, context):
    user_text = update.message.text
    update.message.reply_text(f"Nova Echo: {user_text}")

# Register Handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook Route ---
@app.route(f"/{TOKEN}", methods=['POST'])
def receive_update():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route('/')
def index():
    return "Nova is alive. Webhook is set."

# --- Set Webhook ---
bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

# --- Run App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
