# NovaBot v2 - Superbrain Mode (Sieben Edition)
# Features: Telegram + Groq + OpenRouter integration
# Full LLM personality, memory, and learning interface (text only)

import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Nova")

# --- MEMORY + LOG FILES ---
MEMORY_LOG = "memory_log.json"
EVOLUTION_LOG = "evolution_log.json"

# --- TELEGRAM START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sieben, the world is yours. Superbrain mode is live.")

# --- MESSAGE HANDLER ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    logger.info(f"Message from {user_id}: {user_message}")

    # Process with LLMs
    response = await query_llms(user_message)
    await update.message.reply_text(response)

# --- LLM QUERY LOGIC ---
async def query_llms(prompt):
    # Prioritize OpenRouter (GPT-4 / Claude) fallback to Groq
    try:
        reply = query_openrouter(prompt)
        if reply:
            return reply
    except Exception as e:
        logger.warning(f"OpenRouter failed: {e}")

    try:
        return query_groq(prompt)
    except Exception as e:
        logger.error(f"Groq failed: {e}")
        return "Nova failed to think."

# --- OPENROUTER API ---
def query_openrouter(prompt):
    key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "openrouter/gpt-4",
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

# --- GROQ API (Mistral) ---
def query_groq(prompt):
    key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()['choices'][0]['message']['content']

# --- INIT BOT ---
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Nova is live and thinking.")
    app.run_polling()

if __name__ == '__main__':
    main()
