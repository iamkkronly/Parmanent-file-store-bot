# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import BadRequest

# ---------------- CONFIG ----------------
BOT_TOKEN = "8275025400:AAEyu7Rb8h2bnDGOfBf336yMO5bzFSrS8V8"
DB_CHANNEL_ID = -1002933239181  # Hardcoded DB channel ID
# ----------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# -------- COMMAND HANDLERS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and optional deep link"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "👋 
            Send me any file and I will create a permanent link for it!
            Kaustav Ray                                                         KR Republic                                                      Join here: @filestore4u     @freemovie5u"
        )
        return

    # Deep linking: retrieve file from DB channel
    msg_id = args[0]
    try:
        await context.bot.forward_message(
            chat_id=update.message.chat_id, 
            from_chat_id=DB_CHANNEL_ID, 
            message_id=int(msg_id)
        )
    except BadRequest:
        await update.message.reply_text("⚠️ Failed to retrieve file from DB channel.")
    except Exception as e:
        await update.message.reply_text("⚠️ An unexpected error occurred.")
        logger.error(e)

# -------- MESSAGE HANDLER --------
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward any user message to DB channel and return permanent link"""
    try:
        forwarded_msg = await update.message.forward(chat_id=DB_CHANNEL_ID)
        msg_id = forwarded_msg.message_id
        link = f"https://t.me/{context.bot.username}?start={msg_id}"

        # Optional: send as inline button for convenience
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📂 Get File", url=link)]]
        )
        await update.message.reply_text(
            f"Kaustav Ray                                                         KR Republic                                                      Join here: @filestore4u     @freemovie5u
            ✅ Permanent Link Created:", reply_markup=keyboard
        )
    except BadRequest as e:
        await update.message.reply_text(f"⚠️ Failed to forward message: {e}")
    except Exception as e:
        await update.message.reply_text("⚠️ An unexpected error occurred.")
        logger.error(e)

# -------- MAIN --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))

    # Catch-all handler for all messages/files
    app.add_handler(MessageHandler(filters.ALL, save_message))

    logger.info("Bot started...")
    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)

if __name__ == "__main__":
    main()
