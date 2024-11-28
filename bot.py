
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputTextMessageContent
from telethon import TelegramClient, events

# Bot configuration
BOT_TOKEN = os.environ.get("6228122908:AAEKGwokHIjvYsH6qgthcz5G-sOdL3Aq45o")
API_ID = int(os.environ.get('18979569'))
API_HASH = os.environ.get("45db354387b8122bdf6c1b0beef93743")
SESSION_NAME = "session_generator"

# Create the Pyrogram client
pyrogram_client = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def start():
    await pyrogram_client.start()

    await ask_api_id()
    await ask_api_hash()
    await ask_bot_token_or_phone_number()

async def ask_api_id():
    await pyrogram_client.send_message("me", "Enter your API ID:")
    api_id = await pyrogram_client.listen(InputTextMessageContent)
    return api_id

async def ask_api_hash():
    await pyrogram_client.send_message("me", "Enter your API Hash:")
    api_hash = await pyrogram_client.listen(InputTextMessageContent)
    return api_hash

async def ask_bot_token_or_phone_number():
    buttons = [
        [InlineKeyboardButton("Bot Token", callback_data="bot_token")],
        [InlineKeyboardButton("Phone Number", callback_data="phone_number")]
    ]
    await pyrogram_client.send_message("me", "Select an option:", reply_markup=InlineKeyboardMarkup(buttons))

async def generate_session(bot_token=None, phone_number=None):
    if bot_token:
        # Generate session string using bot token
        await pyrogram_client.send_message("me", "Generating session string using bot token...")
        session_string = await pyrogram_client.generate_session_string(bot_token)
        await pyrogram_client.send_message("me", f"Session string: {session_string}")
    elif phone_number:
        # Send OTP to Telegram and verify
        await pyrogram_client.send_message("me", "Sending OTP to Telegram...")
        otp = await pyrogram_client.send_code(phone_number)
        await pyrogram_client.send_message("me", "Enter the OTP:")
        otp_input = await pyrogram_client.listen(InputTextMessageContent)
        if otp_input == otp:
            # Check 2-step verification
            await pyrogram_client.send_message("me", "Checking 2-step verification...")
            if await pyrogram_client.check_2fa(phone_number):
                # Generate session string
                await pyrogram_client.send_message("me", "Generating session string...")
                session_string = await pyrogram_client.generate_session_string(phone_number)
                await pyrogram_client.send_message("me", f"Session string: {session_string}")
            else:
                await pyrogram_client.send_message("me", "2-step verification is not enabled.")
        else:
            await pyrogram_client.send_message("me", "Invalid OTP.")

@pyrogram_client.on_callback_query()
async def callback_query_handler(_, callback_query):
    if callback_query.data == "bot_token":
        await pyrogram_client.send_message("me", "Enter your bot token:")
        bot_token = await pyrogram_client.listen(InputTextMessageContent)
        await generate_session(bot_token=bot_token)
    elif callback_query.data == "phone_number":
        await pyrogram_client.send_message("me", "Enter your phone number:")
        phone_number = await pyrogram_client.listen(InputTextMessageContent)
        await generate_session(phone_number=phone_number)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start())
