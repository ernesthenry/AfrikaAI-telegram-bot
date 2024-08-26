import re
import os
import time
import telegram
import openai
from app import app
from flask import request
from dotenv import load_dotenv
from app.ai import generate_smart_reply
load_dotenv()
# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API")
URL = os.getenv("BOT_URL")
# Initialize Telegram Bot
TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # Retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Decode the text message
    text = update.message.text.encode('utf-8').decode()
    # For debugging purposes
    print("Received text message:", text)

    if text == "/start":
        # Welcome message
        bot_welcome = """
            Welcome to Msema Kweli bot, a fact-checking assistant to validate
            development agendas and budget allocations for Kenyan county
            governments ensuring they comply with existing policies.
        """
        # Send the welcoming message
        bot.sendChatAction(chat_id=chat_id, action="typing")
        time.sleep(1.5)
        bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)
    else:
        try:
            # Generate AI response
            ai_reply = generate_smart_reply(text)
            # Send AI-generated response
            bot.sendChatAction(chat_id=chat_id, action="typing")
            time.sleep(1.5)
            bot.sendMessage(chat_id=chat_id, text=ai_reply, reply_to_message_id=msg_id)
        except Exception as e:
            print("Error:", e)
            bot.sendMessage(
                chat_id=chat_id,
                text="There was an error processing your request. Please try again.",
                reply_to_message_id=msg_id
            )

    return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "Webhook setup ok"
    else:
        return "Webhook setup failed"

@app.route('/')
def index():
    return 'Bot is running on '+URL