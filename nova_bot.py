
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
import os

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic command handler
def start(update, context):
    update.message.reply_text("Nova is online. Awaiting your command, Sieben.")

def echo(update, context):
    user_text = update.message.text
    if "who am i" in user_text.lower():
        update.message.reply_text("You are Sieben. The world is yours.")
    else:
        update.message.reply_text(f"Echo: {user_text}")

def error(update, context):
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    print("System check complete. Memory loaded.")
    print(f"Time: {datetime.now()}")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

