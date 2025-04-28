

import os

from flask import Flask, request

from telegram import Update, Bot

from telegram.ext import Updater, CommandHandler, Dispatcher, CallbackContext

# Replace with your bot token

BOT_TOKEN = "8013238176:AAFIBhEUUiH8BwBMhi6DG7On_qKj00yCXKc"

app = Flask(__name__)

# Handler for /start command

def start(update: Update, context: CallbackContext) -> None:

    user = update.message.from_user

    update.message.reply_text(f"Hello {user.first_name}! Welcome to the Face Swap Bot. Send a video and a photo to swap faces!")

# Webhook endpoint

@app.route(f"/{BOT_TOKEN}", methods=["POST"])

def webhook():

    update = Update.de_json(request.get_json(force=True), bot)

    dispatcher.process_update(update)

    return "OK", 200

# Initialize bot and dispatcher

bot = Bot(BOT_TOKEN)

updater = Updater(BOT_TOKEN, use_context=True)

dispatcher = updater.dispatcher

# Add /start command handler

dispatcher.add_handler(CommandHandler("start", start))

if __naame__ == "__main__":

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    