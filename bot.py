# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.

"""
Telegram Permanent File Store Bot (Fixed Filters)
"""

import logging
import base64
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================
# CONFIG
# ==========================

TOKEN = base64.b64decode(
    "ODI3NTAyNTQwMDpBQUVKYV9vZ2hLek1hMDZ4VlhWMkc3OE5vSnpNemxDczdSSQ=="
).decode("utf-8")

ADMIN_ID = 7307633923
DB_CHANNEL_ID = None

# ==========================
# LOGGING
# ==========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ==========================
# COMMAND HANDLERS
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "👋 Welcome!\nSend me a file and I’ll give you a permanent sharable link."
        )
        return

    file_msg_id = args[0]
    if not file_msg_id.isdigit():
        await update.message.reply_text("❌ Invalid link parameter.")
        return

    global DB_CHANNEL_ID
    if not DB_CHANNEL_ID:
        await update.message.reply_text("⚠️ DB channel not configured yet.")
        return

    try:
        file_msg = await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=DB_CHANNEL_ID,
            message_id=int(file_msg_id),
        )
        await update.message.reply_text("✅ Here’s your file:", reply_to_message_id=file_msg.message_id)
    except Exception as e:
        logger.error(f"Error fetching file: {e}")
        await update.message.reply_text("⚠️ Couldn’t fetch the file. Ask the admin.")


async def setdb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /setdb <channel_id>")
        return

    global DB_CHANNEL_ID
    DB_CHANNEL_ID = int(context.args[0])
    await update.message.reply_text(f"✅ DB channel set to `{DB_CHANNEL_ID}`", parse_mode="Markdown")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global DB_CHANNEL_ID
    if not DB_CHANNEL_ID:
        await update.message.reply_text("⚠️ DB channel not set. Ask the admin to run /setdb.")
        return

    file_message = update.message
    try:
        sent = await file_message.forward(chat_id=DB_CHANNEL_ID)
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={sent.message_id}"

        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open File", url=link)]])
        await update.message.reply_text(
            f"✅ File stored successfully!\nHere’s your permanent link:\n{link}",
            reply_markup=kb,
        )
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        await update.message.reply_text("⚠️ Failed to save file.")


# ==========================
# MAIN
# ==========================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setdb", setdb))

    app.add_handler(
        MessageHandler(
            filters.Document.ALL | filters.VIDEO | filters.AUDIO | filters.PHOTO,
            handle_file,
        )
    )

    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)


if __name__ == "__main__":
    main()
