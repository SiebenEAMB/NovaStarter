import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
# --- Initialize Bot ---
app = Flask(__name__)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.bot = application.bot

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am Nova.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Echo: {user_message}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Webhook Setup ---
@app.route("/", methods=["GET"])
def index():
    return "Nova webhook active."

@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), app.bot)
    await application.process_update(update)
    return "ok"

@app.before_first_request
def init_webhook():
    app.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")

# --- Run Flask ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(application.initialize())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
