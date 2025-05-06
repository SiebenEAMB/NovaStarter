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
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Initialize Flask and Bot ---
app = Flask(__name__)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
bot = application.bot

# --- Telegram Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am Nova.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f"Echo: {user_message}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask Routes ---
@app.route("/", methods=["GET"])
def index():
    return "Nova webhook active."

@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        print("📩 Incoming update:", data)

        update = Update.de_json(data, bot)
        print("🛠 Update object created.")

        await application.process_update(update)
        print("✅ Update processed successfully.")

        return "ok"
    except Exception as e:
        import traceback
        print("❌ Webhook error:", str(e))
        traceback.print_exc()
        return "error", 500
        
# --- Startup: Set Webhook & Run Server ---
async def main():
    await application.initialize()
    await application.start()  # REQUIRED or messages won't process
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")
    await application.updater.start_polling()  # <-- ACTIVATE dispatcher
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    asyncio.run(main())
