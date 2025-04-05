import os
import json
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
from translate import TRANSLATIONS
from db import Session, get_user
from prompts import DEFAULT_PROMPTS

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHITELIST_IDS = set(item.strip() for item in os.getenv("WHITELIST_IDS", "").split(","))

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Translation helper
def t(key, user):
    lang = user.language or "en"
    return TRANSLATIONS[lang][key]

# Contact keyboard
def contact_keyboard(user):
    button = KeyboardButton(t("share_contact", user), request_contact=True)
    return ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    user_id = update.effective_user.id
    user = get_user(session, user_id)
    user.language = "en"  # fallback before selection
    session.commit()

    keyboard = [["🇬🇧 English", "فارسی 🇮🇷"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌐 Choose your language:", reply_markup=markup)

# Handle contact (phone auth)
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    contact = update.message.contact
    user_id = update.effective_user.id
    user = get_user(session, user_id)

    phone_number = contact.phone_number
    if phone_number.startswith("0"):
        phone_number = "+49" + phone_number[1:]

    if phone_number in WHITELIST_IDS:
        user.verified = True
        session.commit()
        await update.message.reply_text(t("phone_verified", user), reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(t("phone_denied", user))

# Unified handler: language select + GPT chat
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    user_id = update.effective_user.id
    text = update.message.text
    user = get_user(session, user_id)

    if not user.verified:
        if "English" in text:
            user.language = "en"
        elif "فارسی" in text or "Persian" in text:
            user.language = "fa"
        else:
            await update.message.reply_text("❌ Invalid choice.")
            return

        username = f"@{update.effective_user.username}" if update.effective_user.username else None
        if username in WHITELIST_IDS:
            user.verified = True
            session.commit()
            await update.message.reply_text(t("welcome", user).format(name=username), reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(t("not_authorized", user), reply_markup=contact_keyboard(user))
        return

    # User is verified: continue chat with GPT
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        history = json.loads(user.history or "[]")
        history.append({"role": "user", "content": text})
        history = history[-20:]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": DEFAULT_PROMPTS[user.language]}] + history,
            temperature=0.7,
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

        history.append({"role": "assistant", "content": reply})
        user.history = json.dumps(history)
        session.commit()

    except Exception as e:
        print(f"OpenAI API error: {e}")
        await update.message.reply_text("⚠️ An error occurred while talking to GPT.")

# /reset command
async def reset_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session()
    user = get_user(session, update.effective_user.id)
    user.history = "[]"
    session.commit()
    await update.message.reply_text("🧹 Conversation history reset.")

# Main setup
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_chat))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()