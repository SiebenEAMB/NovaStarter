
# nova_bot.py — Sieben Edition
# Version 1.0.0

import os
import time
import json
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load memory and evolution logs
def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

memory_log = load_json("memory_log.json")
evolution_log = load_json("evolution_log.json")

# Nova's intro + boot ping
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    greeting = f"Sieben, the world is yours."
System check complete. Memory loaded.
Time: {datetime.now()}"
    await update.message.reply_text(greeting)

    evolution_log.append({
        "timestamp": str(datetime.now()),
        "evolution_type": "Boot",
        "details": "Nova initialized and greeted Sieben",
        "triggered_by": user.username,
        "version": "Nova v1.0.0"
    })
    save_json("evolution_log.json", evolution_log)

# Simple command test
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    response = f"Message received: {text}"
    await update.message.reply_text(response)

    memory_log.append({
        "timestamp": str(datetime.now()),
        "user": update.message.from_user.username,
        "message": text,
        "response": response,
        "memory_flags": ["basic_input"]
    })
    save_json("memory_log.json", memory_log)

# Telegram bot runner
def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    print("Nova is now online.")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
