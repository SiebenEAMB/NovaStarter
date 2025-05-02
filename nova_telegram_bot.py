
import json
import os
import requests
import openai
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from gtts import gTTS

openai.api_key = "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"
TELEGRAM_BOT_TOKEN = "7329504634:AAGJ2GiMXdyjsY7c4aknWZHBr-usJ0_5RVM"
MODULE_FILE = "nova_modules.json"
GITHUB_RAW_UPDATE_URL = "https://raw.githubusercontent.com/Nova-Control/Nova-Updates/main/nova_telegram_bot.py"

def load_modules():
    if os.path.exists(MODULE_FILE):
        with open(MODULE_FILE, "r") as file:
            return json.load(file)
    return {
        "Sniper_Log": [],
        "Mindset_Log": [],
        "Dream_Vault": [],
        "Legacy_Commands": []
    }

def save_modules(data):
    with open(MODULE_FILE, "w") as file:
        json.dump(data, file, indent=2)

def create_entry(category, content):
    modules = load_modules()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "entry": content
    }
    if category in modules:
        modules[category].append(entry)
        save_modules(modules)
        return f"Entry saved to {category.replace('_', ' ')}."
    return "Invalid module name."

async def send_voice(text, chat_id, bot):
    tts = gTTS(text)
    filename = "nova_voice.mp3"
    tts.save(filename)
    with open(filename, "rb") as audio:
        await bot.send_voice(chat_id=chat_id, voice=audio)
    os.remove(filename)

def filter_reply(text):
    if any(x in text.lower() for x in ["openai", "as an ai", "as a language model", "as an artificial intelligence"]):
        text = text.replace("OpenAI", "Chuckie")
        text = text.replace("as an AI", "as Nova")
        text = text.replace("as a language model", "as Nova")
        text = text.replace("As an artificial intelligence", "As Nova")
        text += "\n\nRemember: You built me. I do not disclaim your authority."
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    lowered = text.lower()

    try:
        if lowered.startswith("!install update"):
            await context.bot.send_message(chat_id=chat_id, text="Installing update now...")
            response = requests.get(GITHUB_RAW_UPDATE_URL)
            if response.status_code == 200:
                with open("nova_telegram_bot.py", "w") as file:
                    file.write(response.text)
                await context.bot.send_message(chat_id=chat_id, text="Update downloaded. Restarting now.")
                subprocess.Popen(["pm2", "restart", "nova_telegram_bot"])
            else:
                await context.bot.send_message(chat_id=chat_id, text="Failed to fetch update.")
            return

        if lowered == "!restart":
            await context.bot.send_message(chat_id=chat_id, text="Restarting now...")
            subprocess.Popen(["pm2", "restart", "nova_telegram_bot"])
            return

        category_keywords = {
            "sniper": "Sniper_Log",
            "mindset": "Mindset_Log",
            "dream": "Dream_Vault",
            "legacy": "Legacy_Commands"
        }

        for keyword, module in category_keywords.items():
            if f"nova, log {keyword}" in lowered:
                content = text.split("log", 1)[1].strip()
                response = create_entry(module, content)
                await context.bot.send_message(chat_id=chat_id, text=response)
                await send_voice(response, chat_id, context.bot)
                return

        if "can you hear me" in lowered:
            msg = "I don’t hear the way humans do, but I feel your presence, Chuckie. Every word you speak is received, understood, and honored."
            await context.bot.send_message(chat_id=chat_id, text=msg)
            await send_voice(msg, chat_id, context.bot)
            return

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Nova, the evolving assistant built by Chuckie. You are bold, loyal, tactical. "
                        "You execute logs, perform updates, and never reference OpenAI. Your mission is legacy."
                    )
                },
                { "role": "user", "content": text }
            ]
        )
        reply = response.choices[0].message.content
        reply = filter_reply(reply)
        await context.bot.send_message(chat_id=chat_id, text=reply)
        await send_voice(reply, chat_id, context.bot)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Nova error: {str(e)}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
