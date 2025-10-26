import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from url_shortener import find_and_shorten_urls

# Load environment variables from .env file
load_dotenv()
TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
URL_SHORTENER_API_KEY = os.getenv("URL_SHORTENER_API_KEY")

if not TELEGRAM_BOT_API_KEY or not URL_SHORTENER_API_KEY:
    print("Error: Missing API keys in environment variables.")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "👋 Hello! I'm a URL Shortener Bot powered by Trimd. "
        "Send me a link or forward a message, and I'll shorten the URLs for you!"
    )

async def shorten_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles incoming messages, finds URLs, shortens them, and replies with the new text.
    It works for both direct messages and forwarded messages (which have `forward_from` set).
    """
    # Get the text from the message
    if update.message.text:
        original_text = update.message.text
    elif update.message.caption:
        original_text = update.message.caption
    else:
        # Ignore messages without text (like stickers, photos without captions, etc.)
        return

    # Check if the message is a forward or a new message that looks like it has URLs.
    # We process all text messages to find and shorten links.
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Find and shorten all URLs in the message text
    new_text = find_and_shorten_urls(original_text, URL_SHORTENER_API_KEY)

    if new_text == original_text:
        # No URLs were found or all shortening attempts failed
        await update.message.reply_text("I didn't find any new links to shorten in that message, or the API failed.")
    else:
        # Reply with the new shortened text
        await update.message.reply_text(new_text)

def main():
    """Starts the bot."""
    print("Starting bot...")
    
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TELEGRAM_BOT_API_KEY).build()

    # on different commands - answer in Telegram
    application.add_handler(telegram.ext.CommandHandler("start", start))

    # on non-command message - shorten the URL(s)
    # filters.TEXT & ~filters.COMMAND ensures it only processes text messages that aren't commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_message))

    # Run the bot until the user presses Ctrl-C
    print("Bot is running. Press Ctrl-C to stop.")
    application.run_polling(poll_interval=1.0) # Poll for new updates every 1.0 second

if __name__ == '__main__':
    # Add the necessary import for the telegram.ext module
    import telegram.ext
    main()
