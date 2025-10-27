import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, # Changed from ApplicationBuilder
    ContextTypes, 
    MessageHandler, 
    filters,
    CommandHandler
)
from url_shortener import find_and_shorten_urls

# Set up logging for better visibility during deployment
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
URL_SHORTENER_API_KEY = os.getenv("URL_SHORTENER_API_KEY")

# Environment variables required for Webhook deployment
# Render automatically provides PORT. WEBHOOK_URL must be set in Render's environment settings.
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
PORT = int(os.environ.get("PORT", "8080")) # Get the port provided by the host

if not TELEGRAM_BOT_API_KEY or not URL_SHORTENER_API_KEY or not WEBHOOK_URL:
    logger.error("Configuration Error: One or more required environment variables (API keys, WEBHOOK_URL) are missing.")
    # We do not exit(1) here because Gunicorn must successfully import the module.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    await update.message.reply_text(
        "👋 Hello! I'm a URL Shortener Bot powered by Trimd. "
        "Send me a link or forward a message, and I'll shorten the URLs for you!"
    )

async def shorten_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles incoming messages, finds URLs, shortens them, and replies with the new text.
    """
    if update.message.text:
        original_text = update.message.text
    elif update.message.caption:
        original_text = update.message.caption
    else:
        # Ignore messages without text
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Find and shorten all URLs in the message text
    new_text = find_and_shorten_urls(original_text, URL_SHORTENER_API_KEY)

    if new_text == original_text:
        await update.message.reply_text("I didn't find any new links to shorten in that message, or the API failed.")
    else:
        await update.message.reply_text(new_text)

# --- WEBHOOK ENTRY POINT FOR GUNICORN ---
def run_bot():
    """
    Initializes and runs the bot in Webhook mode.
    This function is called by Gunicorn to start the web service.
    """
    if not TELEGRAM_BOT_API_KEY or not WEBHOOK_URL:
        # If configuration is missing, return a dummy function to prevent Gunicorn crash
        return lambda environ, start_response: (
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')]), 
            [b'Configuration Error: Check API Keys and WEBHOOK_URL']
        )
    
    logger.info(f"Starting Webhook on port {PORT}...")
    
    # Create the Application
    # Using Application.builder() instead of ApplicationBuilder() for modern usage
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_message))

    # Configure Webhook settings
    application.run_webhook(
        listen="0.0.0.0",        # Crucial for Render/cloud deployment
        port=PORT,
        url_path="",             # Empty path means Telegram hits the root URL
        webhook_url=WEBHOOK_URL  # The public URL Telegram will send updates to
    )
    
    # run_webhook returns the WSGI application object needed by Gunicorn
    return application.updater.app

if __name__ == '__main__':
    # This block is for local polling-based testing only
    if TELEGRAM_BOT_API_KEY:
        logger.info("Running locally with polling for testing...")
        application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_message))
        application.run_polling(poll_interval=1.0)
    else:
        logger.error("Cannot run locally: TELEGRAM_BOT_API_KEY is missing.")
