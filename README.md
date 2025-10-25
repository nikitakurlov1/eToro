# Telegram Bot with Terms of Service Agreement

This Telegram bot displays terms of service when a user clicks the Start button and requires them to agree before using the bot.

## Features

- Sends a welcome message with terms of service explanation
- Provides two buttons:
  1. "Прочитать" - Opens the terms of service link (https://telegra.ph/Usloviya-servisa-eTron-10-23)
  2. "Прочитал и согласен✅" - Confirms agreement and enables full bot functionality

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram
2. Copy the bot token
3. Replace `'YOUR_TOKEN_HERE'` in [bot.py](file:///Users/nikitakurlov/eToro/bot.py) with your actual bot token
4. Install the required dependencies:
   ```
   pip install python-telegram-bot
   ```

## Running the Bot

```bash
python bot.py
```

## How It Works

1. When a user sends `/start` to the bot, they receive a welcome message explaining the terms of service
2. The user can either:
   - Click "Прочитать" to open the terms of service link
   - Click "Прочитал и согласен✅" to confirm they've read and agreed to the terms
3. After agreeing, the user receives a confirmation message and can use the bot's full functionality