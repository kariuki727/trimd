# @trimdbot on Telegram by Trimd.cc
A free link shortener bot to shorten a long link and create a short URL easy to share.

# Telegram URL Shortener Bot

This Telegram bot shortens URLs and replaces all links in forwarded messages with their shortened versions. It uses the **Trimd API** for URL shortening and the **Telegram Bot API** for interactions.

## Features
* Shortens URLs sent by the user.
* Replaces URLs in forwarded messages with shortened versions.
* Uses the **Trimd URL shortening API**.

## Installation

Follow these steps to set up and run the project locally.

### Prerequisites
You need **Python 3.x** installed.

### Setup

1.  **Signup on Trimd**:
    * Signup on [https://trimd.cc](https://trimd.cc).
    * Visit the API page and copy your developer API key.

2.  **Create a Telegram Bot**:
    * Create a bot on Telegram via **BotFather** and copy the API token.

3.  **Configure Environment Variables**:
    * Create a file named `.env` in the root directory (using `.env.example` as a template).
    * Add your keys to the file:
        ```
        URL_SHORTENER_API_KEY=your_url_shortener_api_key
        TELEGRAM_BOT_API_KEY=your_telegram_bot_api_key
        ```

4.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/bricekainc/trimd.git](https://github.com/bricekainc/trimd.git)
    cd trimd
    ```

5.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

6.  **Run the Bot**:
    ```bash
    python bot.py
    ```
