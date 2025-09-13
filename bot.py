# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.

import logging
import random
import string
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import BadRequest

# ---------------- CONFIG ----------------
BOT_TOKEN = "8275025400:AAEyu7Rb8h2bnDGOfBf336yMO5bzFSrS8V8"
DB_CHANNEL_ID = -1002933239181  # Fixed DB channel ID
PROMO_TEXT = (
    "\n\n🌟 Kaustav Ray | KR Republic\n"
    "Join here: @filestore4u | @freemovie5u"
)
# ----------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _random_suffix(letters_len: int = 28, digits_len: int = 20) -> str:
    """Generate a random suffix: letters followed by digits (noise)."""
    letters = "".join(random.choices(string.ascii_letters, k=letters_len))
    digits = "".join(random.choices(string.digits, k=digits_len))
    return letters + digits


# -------- COMMAND HANDLERS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and optional deep link."""
    args = context.args
    if not args:
        await update.message.reply_text(
            f"👋 Send me any file and I will create a permanent link for it!{PROMO_TEXT}"
        )
        return

    raw = args[0]
    # Extract leading digits only (message_id).
    m = re.match(r"^(\d+)", raw)
    if not m:
        await update.message.reply_text(f"⚠️ Invalid link parameter.{PROMO_TEXT}")
        return

    msg_id = int(m.group(1))
    try:
        await context.bot.copy_message(
            chat_id=update.message.chat_id,
            from_chat_id=DB_CHANNEL_ID,
            message_id=msg_id
        )
        await update.message.reply_text(PROMO_TEXT)
    except BadRequest:
        await update.message.reply_text(f"⚠️ Failed to retrieve file from DB channel.{PROMO_TEXT}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ An unexpected error occurred.{PROMO_TEXT}")
        logger.error(e)


# -------- MESSAGE HANDLER --------
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Copy user message to DB channel anonymously and return permanent link with noise suffix."""
    try:
        copied_msg = await context.bot.copy_message(
            chat_id=DB_CHANNEL_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        msg_id = copied_msg.message_id

        suffix = _random_suffix()
        link = f"https://t.me/{context.bot.username}?start={msg_id}{suffix}"

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📂 Get File", url=link),
            InlineKeyboardButton("🔗 Copy Link", url=link)
        ]])

        await update.message.reply_text(
            f"✅ Permanent Link Created:{PROMO_TEXT}\n\n🔗 Direct Link: {link}",
            reply_markup=keyboard
        )
    except BadRequest as e:
        await update.message.reply_text(f"⚠️ Failed to copy message: {e}{PROMO_TEXT}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ An unexpected error occurred.{PROMO_TEXT}")
        logger.error(e)


# -------- MAIN --------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))

    # Catch-all for all files/messages
    app.add_handler(MessageHandler(filters.ALL, save_message))

    logger.info("Bot started...")
    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)


if __name__ == "__main__":
    main()
