# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.

"""
Telegram Permanent File Store Bot

Features:
- Save any file/message sent by user into a DB channel anonymously (no username forwarded).
- Generate permanent share links for saved files.
- Deep-linking: Users can retrieve the file back using generated link.
- Link obfuscation: Adds random meaningless letters before/after message IDs.
- Inline buttons: "Get File" and "Copy Link".
- Promotional text appended everywhere for visibility.

Author: Kaustav Ray
"""

import logging
import random
import string
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.error import BadRequest

# ---------------- CONFIG ----------------
BOT_TOKEN = "8275025400:AAEyu7Rb8h2bnDGOfBf336yMO5bzFSrS8V8"
DB_CHANNEL_ID = -1002933239181  # Predefined DB channel ID
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


# --------- HELPER FUNCTIONS ---------
def _random_letters(n: int = 4) -> str:
    """Return a random lowercase string of length n."""
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


def decorate_msg_id(msg_id: int) -> str:
    """
    Wrap numeric message_id with meaningless random letters before and after.
    Example: abc1234xyz
    """
    prefix = _random_letters(3)
    suffix = _random_letters(3)
    return f"{prefix}{msg_id}{suffix}"


def extract_message_id(decorated: str) -> int | None:
    """
    Extract first sequence of digits in decorated string and return as int.
    Returns None if no digits found.
    """
    m = re.search(r"\d+", decorated)
    if not m:
        return None
    try:
        return int(m.group(0))
    except ValueError:
        return None


# --------- COMMAND HANDLERS ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command handler.
    - If no args: Show welcome + promo.
    - If args: Treat as deep link, extract file from DB channel.
    """
    args = context.args
    if not args:
        await update.message.reply_text(
            f"👋 Send me any file and I will create a permanent link for it!{PROMO_TEXT}"
        )
        return

    decorated_id = args[0]
    msg_id = extract_message_id(decorated_id)
    if msg_id is None:
        await update.message.reply_text(f"❌ Invalid link format.{PROMO_TEXT}")
        return

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
        await update.message.reply_text(f"⚠️ Unexpected error occurred.{PROMO_TEXT}")
        logger.error("Error retrieving file: %s", e)


# --------- MESSAGE HANDLER ---------
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle any user message (files, docs, videos, etc.).
    - Copy to DB channel anonymously.
    - Generate decorated link.
    - Reply with inline keyboard & direct link + promo.
    """
    try:
        copied_msg = await context.bot.copy_message(
            chat_id=DB_CHANNEL_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        real_msg_id = copied_msg.message_id
        decorated = decorate_msg_id(real_msg_id)
        link = f"https://t.me/{context.bot.username}?start={decorated}"

        # Inline buttons
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
        await update.message.reply_text(f"⚠️ Unexpected error occurred.{PROMO_TEXT}")
        logger.error("Error saving message: %s", e)


# --------- MAIN ---------
def main():
    """Start the bot."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))

    # Catch-all for any message/file
    app.add_handler(MessageHandler(filters.ALL, save_message))

    logger.info("Bot started successfully...")
    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)


if __name__ == "__main__":
    main()
