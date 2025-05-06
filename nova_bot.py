
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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
bot = application.bot

async def query_llms(prompt: str) -> str:
    try:
        # Try Groq first
        groq_headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        groq_data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "mixtral-8x7b-32768",
            "temperature": 0.7
        }
        response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                 headers=groq_headers, json=groq_data)
        if response.ok:
            return response.json()["choices"][0]["message"]["content"]

        # Then try OpenRouter
        or_headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        or_data = {
            "model": "mistralai/mixtral-8x7b",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=or_headers, json=or_data)
        if response.ok:
            return response.json()["choices"][0]["message"]["content"]

        return "All LLM providers failed to respond."

    except Exception as e:
        return f"LLM Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nova's new brain is live — talk to me!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    response = await query_llms(user_message)
    await update.message.reply_text(response)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/", methods=["GET"])
def index():
    return "Nova webhook alive."

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
    print("🧠 Nova running Groq/OpenRouter brain.")

if __name__ == "__main__":
    import threading
    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(main())
