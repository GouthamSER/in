from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from pyrogram import Client as PyroClient
from pyrogram.errors import SessionPasswordNeeded
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Bot configuration
BOT_TOKEN = "6228122908:AAEKGwokHIjvYsH6qgthcz5G-sOdL3Aq45o"  # Replace with your bot token
bot_data = {}  # Temporary storage for user interaction steps

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Sends a message with inline buttons for selecting the session type
    await update.message.reply_text(
        "Welcome to the Session String Generator Bot!\n\n"
        "Click a button below to generate your session string.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Generate Telethon String", callback_data="telethon")],
            [InlineKeyboardButton("Generate Pyrogram String", callback_data="pyrogram")]
        ])
    )

# Button selection handler
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "telethon":
        bot_data[user_id] = {"type": "telethon"}
        await query.edit_message_text("You selected Telethon. Please enter your **API ID**.")
    elif query.data == "pyrogram":
        bot_data[user_id] = {"type": "pyrogram"}
        await query.edit_message_text("You selected Pyrogram. Please enter your **API ID**.")

# Handle user input for API ID, API Hash, and phone number
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in bot_data:
        await update.message.reply_text("Please start by clicking /start.")
        return

    user_step = bot_data[user_id].get("step", "api_id")

    if user_step == "api_id":
        bot_data[user_id]["api_id"] = update.message.text
        bot_data[user_id]["step"] = "api_hash"
        await update.message.reply_text("Great! Now enter your **API Hash**.")
    elif user_step == "api_hash":
        bot_data[user_id]["api_hash"] = update.message.text
        bot_data[user_id]["step"] = "phone_number"
        await update.message.reply_text("Perfect! Now enter your **phone number** (with country code).")
    elif user_step == "phone_number":
        bot_data[user_id]["phone_number"] = update.message.text
        session_type = bot_data[user_id]["type"]
        if session_type == "telethon":
            await generate_telethon_session(update, context, user_id)
        elif session_type == "pyrogram":
            await generate_pyrogram_session(update, context, user_id)

# Generate Telethon session string
async def generate_telethon_session(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    api_id = bot_data[user_id]["api_id"]
    api_hash = bot_data[user_id]["api_hash"]
    phone_number = bot_data[user_id]["phone_number"]

    client = TelegramClient("telethon_session", int(api_id), api_hash)

    try:
        await client.start(phone=phone_number)
        if await client.is_user_authorized():
            session_string = client.session.save()
            await update.message.reply_text(f"Your Telethon Session String:\n\n`{session_string}`\n\nKeep it safe!")
        else:
            # Send OTP request via the bot's PM
            otp_msg = "Two-step verification is enabled. Please provide the **OTP** sent to your Telegram app."
            await update.message.reply_text(otp_msg)
            bot_data[user_id]["step"] = "otp"
    except SessionPasswordNeededError:
        await update.message.reply_text("Two-step verification is enabled. Please provide your password.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
    finally:
        await client.disconnect()

# Handle OTP input for Telethon
async def handle_otp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in bot_data or bot_data[user_id].get("step") != "otp":
        return  # Ignore if not expecting OTP

    otp = update.message.text.strip()  # Get OTP entered by the user

    api_id = bot_data[user_id]["api_id"]
    api_hash = bot_data[user_id]["api_hash"]
    phone_number = bot_data[user_id]["phone_number"]

    client = TelegramClient("telethon_session", int(api_id), api_hash)

    try:
        await client.start(phone=phone_number, password=otp)
        session_string = client.session.save()
        await update.message.reply_text(f"Your Telethon Session String:\n\n`{session_string}`\n\nKeep it safe!")
    except Exception as e:
        await update.message.reply_text(f"Failed to authenticate with OTP: {e}")
    finally:
        await client.disconnect()
        bot_data.pop(user_id, None)

# Generate Pyrogram session string
async def generate_pyrogram_session(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    api_id = bot_data[user_id]["api_id"]
    api_hash = bot_data[user_id]["api_hash"]
    phone_number = bot_data[user_id]["phone_number"]

    client = PyroClient("pyrogram_session", api_id=int(api_id), api_hash=api_hash)

    try:
        await client.start(phone_number)
        if client.is_user_authorized():
            session_string = client.export_session_string()
            await update.message.reply_text(f"Your Pyrogram Session String:\n\n`{session_string}`\n\nKeep it safe!")
        else:
            await update.message.reply_text("Failed to authenticate. Please check your credentials and try again.")
    except SessionPasswordNeeded:
        await update.message.reply_text("Two-step verification is enabled. Please provide your password.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
    finally:
        await client.stop()
        bot_data.pop(user_id, None)

# Main function
def main():
    # Create the application and pass in your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add the handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_otp_input))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
