# © 2025 Kaustav Ray. All rights reserved.
# Licensed under the MIT License.

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ✅ Your Bot Token (hardcoded, as you asked)
BOT_TOKEN = "8275025400:AAEyu7Rb8h2bnDGOfBf336yMO5bzFSrS8V8"

# ✅ Admin ID
ADMIN_ID = 7307633923

# ✅ DB Channel (set later via /setdb)
DB_CHANNEL_ID = None

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ------------------- HANDLERS -------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.mention_html()} 👋\n\n"
        f"Welcome to the Permanent File Store Bot!\n"
        f"Use /help to see commands.",
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "Here are my commands:\n\n"
        "➡️ /start - Start the bot\n"
        "➕ /clone - Create a new clone of this bot\n"
        "🏞️ /post - Create a new post\n"
        "✍️ /linktxt - Get link for a text message\n"
        "🚀 /referral - Get your referral link\n"
        "ℹ️ /help - Show this help message\n"
        "⚙️ /setdb <channel_id> - Set DB channel\n"
        "📊 /stats - Show bot stats\n"
        "📢 /bcast - Broadcast to users\n"
        "📅 /myplan - Check your plan validity\n"
        "➕ /addfsub - Add Force-Subscribe channel\n"
        "➖ /remfsub - Remove Force-Subscribe channel\n"
        "📋 /listfsub - List Force-Subscribe channels\n"
        "🔒 /fwdlock - Toggle forward protection\n"
        "🗑️ /dltpm - Set PM auto-delete\n"
        "🗑️ /dltfile - Set file auto-delete\n"
        "✍️ /settext - Customize messages\n"
        "ℹ️ /setabout - Set custom 'About' message\n"
        "📝 /setcaption - Set post caption\n"
        "🎥 /settutorial - Set tutorial link\n"
        "📢 /setad - Set ad message\n"
        "✅ /v - Toggle verification\n"
        "🔑 /vapi - Set shortener API key\n"
        "🌐 /vdomain - Set shortener domain\n"
        "⏳ /vduration - Set verification validity\n"
        "👑 /spv - Manage Special VIP users\n",
    )


async def set_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set DB channel (admin only)"""
    global DB_CHANNEL_ID
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Only the admin can use this command.")

    if not context.args:
        return await update.message.reply_text("Usage: /setdb <channel_id>")

    try:
        DB_CHANNEL_ID = int(context.args[0])
        await update.message.reply_text(f"✅ DB channel set to `{DB_CHANNEL_ID}`")
    except ValueError:
        await update.message.reply_text("❌ Invalid channel ID.")


async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save any file to DB channel and return permanent link"""
    global DB_CHANNEL_ID
    if not DB_CHANNEL_ID:
        return await update.message.reply_text("⚠️ DB channel not set. Use /setdb first.")

    # Forward file to DB channel
    file_msg = await update.message.forward(DB_CHANNEL_ID)
    file_id = file_msg.message_id

    # Permanent link with message ID
    link = f"https://t.me/{context.bot.username}?start={file_id}"
    await update.message.reply_text(
        f"✅ File saved!\nPermanent link: {link}",
        disable_web_page_preview=True,
    )


# ------------------- MAIN -------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("setdb", set_db))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Audio.ALL, save_file))

    logger.info("Bot started...")
    app.run_polling(poll_interval=1, timeout=10, drop_pending_updates=True)


if __name__ == "__main__":
    main()
