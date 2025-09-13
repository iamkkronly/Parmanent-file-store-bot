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
ADMIN_IDS = [7307633923]
DB_CHANNEL_ID = None  # set via /setdb
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
            "👋 Send me any file and I will create a permanent link for it!"
        )
        return

    # Deep linking: retrieve file from DB channel
    msg_id = args[0]
    try:
        msg = await context.bot.forward_message(
            chat_id=update.message.chat_id, 
            from_chat_id=DB_CHANNEL_ID, 
            message_id=int(msg_id)
        )
    except BadRequest:
        await update.message.reply_text("⚠️ Failed to retrieve file from DB channel.")
    except Exception as e:
        await update.message.reply_text("⚠️ An unexpected error occurred.")
        logger.error(e)

async def setdb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the DB channel (admin only)"""
    global DB_CHANNEL_ID
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⚠️ You are not allowed to set the DB channel.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /setdb <channel_id>")
        return
    try:
        DB_CHANNEL_ID = int(context.args[0])
        await update.message.reply_text(f"✅ DB channel set to `{DB_CHANNEL_ID}`")
    except ValueError:
        await update.message.reply_text("⚠️ Invalid channel ID.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show DB channel info (admin only)"""
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⚠️ You are not allowed to see stats.")
        return
    try:
        chat = await context.bot.get_chat(DB_CHANNEL_ID)
        await update.message.reply_text(
            f"DB Channel Info:\nTitle: {chat.title}\nType: {chat.type}"
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Failed to fetch stats.")
        logger.error(e)

# -------- MESSAGE HANDLER --------
async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward any user message to DB channel and return permanent link"""
    global DB_CHANNEL_ID
    if DB_CHANNEL_ID is None:
        await update.message.reply_text("⚠️ DB channel is not set. Use /setdb first.")
        return
    try:
        forwarded_msg = await update.message.forward(chat_id=DB_CHANNEL_ID)
        msg_id = forwarded_msg.message_id
        link = f"https://t.me/{context.bot.username}?start={msg_id}"

        # Optional: send as inline button for convenience
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📂 Get File", url=link)]]
        )
        await update.message.reply_text(
            f"✅ Permanent Link Created:", reply_markup=keyboard
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
    app.add_handler(CommandHandler("setdb", setdb))
    app.add_handler(CommandHandler("stats", stats))

    # Catch-all handler for all messages/files
    app.add_handler(MessageHandler(filters.ALL, save_message))

    logger.info("Bot started...")
    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)

if __name__ == "__main__":
    main()
