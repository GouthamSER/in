import logging
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an Instaloader instance
L = instaloader.Instaloader()

# Define a function to download Instagram posts
async def download_instagram_post(username: str):
    try:
        # Download the post
        post = instaloader.Post.from_shortcode(L.context, username)
        file_path = f"downloads/{username}.jpg"  # Save as JPG (can handle multiple formats)
        L.download_post(post, target=file_path)
        return file_path
    except Exception as e:
        logger.error(f"Error downloading post: {e}")
        return None

# Define a function to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi! Send me an Instagram post URL, and I\'ll download it for you.')

# Define a function to handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    if 'instagram.com' in user_text:
        try:
            # Extract the post shortcode (assuming the URL is in a valid format)
            shortcode = user_text.split("/")[-2]  # Getting the shortcode from the URL
            
            # Download the post
            file_path = await download_instagram_post(shortcode)
            if file_path:
                await update.message.reply_text(f"Here is your Instagram post: {file_path}")
                with open(file_path, 'rb') as file:
                    await update.message.reply_document(file)
            else:
                await update.message.reply_text("Failed to download the post.")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
    else:
        await update.message.reply_text("Please send a valid Instagram post URL.")

# Main function to run the bot
async def main() -> None:
    # Replace with your own bot token
    TOKEN = '6228122908:AAEKGwokHIjvYsH6qgthcz5G-sOdL3Aq45o'

    # Create the Application and pass the bot token
    application = Application.builder().token(TOKEN).build()

    # Add command handler for '/start'
    application.add_handler(CommandHandler("start", start))

    # Add handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
