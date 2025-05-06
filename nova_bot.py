import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from flask import Flask, request

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# Basic command and message handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am Nova.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Echo: {user_message}")

# Flask route to verify webhook
@app.route("/", methods=["GET"])
def index():
    return "Nova webhook is set."

async def setup_bot():
    app_ = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app_.add_handler(CommandHandler("start", start))
    app_.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Set webhook
    webhook_set = await app_.bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set: {webhook_set}")

    app_.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_bot())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
