import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, 
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
# Note: .env files are only used locally. On Render, environment variables are set in the dashboard.
load_dotenv()
TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
URL_SHORTENER_API_KEY = os.getenv("URL_SHORTENER_API_KEY")

# Environment variables required for Webhook deployment
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
PORT = int(os.environ.get("PORT", "8080"))

if not TELEGRAM_BOT_API_KEY or not URL_SHORTENER_API_KEY or not WEBHOOK_URL:
    logger.error("Configuration Error: One or more required environment variables (API keys, WEBHOOK_URL) are missing.")

async def post_init(application: Application) -> None:
    """
    Sets the webhook once the Application object is initialized.
    """
    if WEBHOOK_URL and TELEGRAM_BOT_API_KEY:
        try:
            # Set the public URL for Telegram to send updates to
            await application.bot.set_webhook(url=WEBHOOK_URL)
            logger.info(f"Successfully set webhook to: {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"Failed to set webhook URL: {e}")

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
        return

    # Check if API key is available before making API call
    if not URL_SHORTENER_API_KEY:
        await update.message.reply_text("Error: URL Shortener API Key is missing. Cannot shorten links.")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    new_text = find_and_shorten_urls(original_text, URL_SHORTENER_API_KEY)

    if new_text == original_text:
        await update.message.reply_text("I didn't find any new links to shorten in that message, or the API failed.")
    else:
        await update.message.reply_text(new_text)

# --- WSGI FACTORY FUNCTION ---
def _initialize_bot_wsgi():
    """
    Initializes and returns the combined WSGI application (Homepage + Telegram Bot).
    This function is called once when the module loads.
    """
    if not TELEGRAM_BOT_API_KEY or not WEBHOOK_URL:
        # If configuration is missing, return a dummy function for Gunicorn
        logger.error("Configuration missing. Returning 500 handler.")
        return lambda environ, start_response: (
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')]), 
            [b'Configuration Error: Check API Keys and WEBHOOK_URL environment variables.']
        )
    
    logger.info(f"Starting Webhook initialization on port {PORT}...")
    
    # 1. Create the Application and register the post_init hook
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).post_init(post_init).build()

    # 2. Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shorten_message))

    # 3. Configure Webhook settings
    # This prepares the Application to receive webhooks from Telegram
    application.run_webhook(
        listen="0.0.0.0",        
        port=PORT,
        url_path="",             
        webhook_url=WEBHOOK_URL
    )
    
    # Get the Telegram bot's core WSGI application
    telegram_wsgi_app = application.updater.app

    # Define the final WSGI app to be returned to Gunicorn
    def combined_app(environ, start_response):
        """Routes requests between the homepage (GET /) and the Telegram bot (POST /)."""
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')

        # Check for the homepage request (GET request to the root URL)
        if path == '/' and method == 'GET':
            # Serve the simple homepage HTML
            html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Trimd URL Shortener Bot</title>
                    <style>
                        body {{ font-family: sans-serif; text-align: center; padding: 50px; background-color: #f0f4f8; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }}
                        h1 {{ color: #007bff; margin-bottom: 20px; }}
                        .explanation {{ font-size: 1.1em; line-height: 1.6; margin-bottom: 30px; text-align: left; padding: 0 20px; }}
                        .btn {{ 
                            background-color: #007bff; color: white; padding: 12px 25px; 
                            text-decoration: none; border-radius: 8px; font-weight: bold; 
                            transition: background-color 0.3s; display: inline-block; 
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                        }}
                        .btn:hover {{ background-color: #0056b3; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Trimd URL Shortener Telegram Bot</h1>
                        <div class="explanation">
                            <p>This server is running the webhook backend for the URL shortening bot. It uses the Trimd API to turn long, messy links into short, shareable ones.</p>
                            
                            <h2>How to Use It:</h2>
                            <ol style="padding-left: 20px;">
                                <li>Click the button below to open the chat.</li>
                                <li>Send the bot any message containing one or more links.</li>
                                <li>The bot will reply instantly with the same message, but all detected URLs will be shortened!</li>
                            </ol>
                        </div>
                        <a href="https://t.me/trimdbot" class="btn" target="_blank">
                            Start Chatting with the Bot
                        </a>
                    </div>
                </body>
                </html>
            """
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [html_content.encode('utf-8')]
        
        # All other requests (e.g., POST from Telegram) are routed to the bot application
        return telegram_wsgi_app(environ, start_response)

    # Return the combined WSGI application callable
    return combined_app

# --- GUNICORN ENTRY POINT ---
# Gunicorn looks for a WSGI callable named 'app'
app = _initialize_bot_wsgi()


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
