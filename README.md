# @trimdbot on Telegram by Trimd.cc
A free link shortener bot to shorten a long link and create a short URL easy to share.

# Telegram URL Shortener Bot

This Telegram bot shortens URLs and replaces all links in forwarded messages with their shortened versions. It uses the Trimd API for URL shortening and the Telegram Bot API for interactions.

## Features

- Shortens URLs sent by the user.
- Replaces URLs in forwarded messages with shortened versions.
- Uses the Trimd URL shortening API.

## Installation

Follow these steps to set up the project:
1. Signup on https://trimd.cc
2. Visit the api page and copy your developer api key. Add it in your environment variables as '''URL_SHORTENER_API_KEY=your_url_shortener_api_key'''
3. Create a bot on Telegram and copy the api key. Add it in your environment variables as '''TELEGRAM_BOT_API_KEY=your_telegram_bot_api_key'''

### 1. Clone the repository:

```bash
git clone https://github.com/bricekainc/trimd.git
cd trimd
