
import os
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SURFER_API_KEY = os.getenv("SURFER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
bot = application.bot

async def query_llms(prompt: str) -> str:
    try:
        headers = {"Authorization": f"Bearer {SURFER_API_KEY}", "Content-Type": "application/json"}
        response = requests.post("https://api.surferseo.com/v1/chat/completions",
                                 headers=headers, json={"model": "gpt-3.5", "messages": [{"role": "user", "content": prompt}]})
        if response.ok:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")
        else:
            return f"Surfer error: {response.text}"
    except Exception as e:
        return f"Query failed: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nova is now fully awake. Ask me anything.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await query_llms(user_message)
    await update.message.reply_text(response)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/", methods=["GET"])
def index():
    return "Nova Phase 2 is live."

@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        await application.process_update(update)
        return "ok"
    except Exception as e:
        import traceback
        print("❌ Webhook error:", str(e))
        traceback.print_exc()
        return "error", 500

async def main():
    await application.initialize()
    await application.start()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")
    print("🚀 Nova Superbrain online.")

if __name__ == "__main__":
    import threading
    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(main())
