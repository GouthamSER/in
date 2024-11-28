from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from pyrogram import Client as PyroClient
from pyrogram.errors import SessionPasswordNeeded
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Bot configuration
BOT_TOKEN = "6228122908:AAEKGwokHIjvYsH6qgthcz5G-sOdL3Aq45o"  # Replace with your bot token
bot_data = {}  # Temporary storage for user interaction steps

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to the Session String Generator Bot!\n\n"
        "Click a button below to generate your session string.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Generate Telethon String", callback_data="telethon")],
            [InlineKeyboardButton("Generate Pyrogram String", callback_data="pyrogram")]
        ])
    )

# Button selection handler
def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "telethon":
        bot_data[user_id] = {"type": "telethon"}
        query.edit_message_text("You selected Telethon. Please enter your **API ID**.")
    elif query.data == "pyrogram":
        bot_data[user_id] = {"type": "pyrogram"}
        query.edit_message_text("You selected Pyrogram. Please enter your **API ID**.")

# Handle user input for API ID, API Hash, and phone number
def handle_user_input(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in bot_data:
        update.message.reply_text("Please start by clicking /start.")
        return

    user_step = bot_data[user_id].get("step", "api_id")

    if user_step == "api_id":
        bot_data[user_id]["api_id"] = update.message.text
        bot_data[user_id]["step"] = "api_hash"
        update.message.reply_text("Great! Now enter your **API Hash**.")
    elif user_step == "api_hash":
        bot_data[user_id]["api_hash"] = update.message.text
        bot_data[user_id]["step"] = "phone_number"
        update.message.reply_text("Perfect! Now enter your **phone number** (with country code).")
    elif user_step == "phone_number":
        bot_data[user_id]["phone_number"] = update.message.text
        session_type = bot_data[user_id]["type"]
        if session_type == "telethon":
            generate_telethon_session(update, context, user_id)
        elif session_type == "pyrogram":
            generate_pyrogram_session(update, context, user_id)

# Generate Telethon session string
def generate_telethon_session(update: Update, context: CallbackContext, user_id):
    api_id = bot_data[user_id]["api_id"]
    api_hash = bot_data[user_id]["api_hash"]
    phone_number = bot_data[user_id]["phone_number"]

    client = TelegramClient("telethon_session", int(api_id), api_hash)

    try:
        client.start(phone=phone_number)
        if client.is_user_authorized():
            session_string = client.session.save()
            update.message.reply_text(f"Your Telethon Session String:\n\n`{session_string}`\n\nKeep it safe!")
        else:
            update.message.reply_text("Failed to authenticate. Please check your credentials and try again.")
    except SessionPasswordNeededError:
        update.message.reply_text("Two-step verification is enabled. Please provide your password.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")
    finally:
        client.disconnect()
        bot_data.pop(user_id, None)

# Generate Pyrogram session string
def generate_pyrogram_session(update: Update, context: CallbackContext, user_id):
    api_id = bot_data[user_id]["api_id"]
    api_hash = bot_data[user_id]["api_hash"]
    phone_number = bot_data[user_id]["phone_number"]

    client = PyroClient("pyrogram_session", api_id=int(api_id), api_hash=api_hash)

    try:
        client.start(phone_number)
        if client.is_user_authorized():
            session_string = client.export_session_string()
            update.message.reply_text(f"Your Pyrogram Session String:\n\n`{session_string}`\n\nKeep it safe!")
        else:
            update.message.reply_text("Failed to authenticate. Please check your credentials and try again.")
    except SessionPasswordNeeded:
        update.message.reply_text("Two-step verification is enabled. Please provide your password.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {e}")
    finally:
        client.stop()
        bot_data.pop(user_id, None)

# Main function
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_user_input))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
