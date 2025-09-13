# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.

"""
Permanent File Store Bot
------------------------
This bot saves files sent to it and generates permanent sharable links.

Features:
- Supports documents, videos, audios, photos, and animations.
- Returns a permanent link after storing the file.
- Built with python-telegram-bot v20+ (async).
- Includes error handling and logging.
"""

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==============================
# 🔑 Bot Configuration
# ==============================
BOT_TOKEN = "8275025400:AAEyu7Rb8h2bnDGOfBf336yMO5bzFSrS8V8"
BASE_URL = "https://t.me/{username}?start="  # Format for sharable link

# Enable logging for debugging in GitHub Actions
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ==============================
# 📌 Handlers
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the bot is started."""
    await update.message.reply_text(
        "👋 Welcome!\n\nSend me a file (document, video, audio, or photo), "
        "and I'll give you a permanent sharable link."
    )


async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save the uploaded file and return a sharable link.
    Telegram file IDs are permanent, so we generate links using them.
    """
    message = update.message
    file_obj = None

    # Pick file depending on type
    if message.document:
        file_obj = message.document
    elif message.video:
        file_obj = message.video
    elif message.audio:
        file_obj = message.audio
    elif message.photo:
        file_obj = message.photo[-1]  # highest resolution photo
    elif message.animation:
        file_obj = message.animation

    if not file_obj:
        await message.reply_text("⚠️ Unsupported file type.")
        return

    # Get file ID (permanent reference)
    file_id = file_obj.file_id
    sharable_link = f"{BASE_URL.format(username=context.bot.username)}{file_id}"

    await message.reply_text(
        f"✅ File saved!\n\n🔗 Permanent Link:\n{sharable_link}"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors for debugging."""
    logger.error("Exception while handling update:", exc_info=context.error)


# ==============================
# 🚀 Main Function
# ==============================
def main():
    """Start the bot."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))

    # File handler (documents, videos, audios, photos, animations)
    app.add_handler(
        MessageHandler(
            filters.Document.ALL
            | filters.VideoFile.ALL
            | filters.AudioFile.ALL
            | filters.Photo.ALL
            | filters.Animation.ALL,
            save_file,
        )
    )

    # Log errors
    app.add_error_handler(error_handler)

    # Run bot
    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
