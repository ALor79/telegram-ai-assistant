## 📦 Telegram GPT Bot

A Telegram bot that authenticates users based on a whitelist, supports multilingual chat (English and Persian), and integrates with OpenAI's GPT-4o for conversational AI. Chat history is stored using SQLite for persistence.

---

### ✨ Features

- 🔐 Whitelist-based authentication (by `@username` or phone number)
    - Phone numbers must start with '+' the country code 
- 🌍 Language selection (English 🇬🇧 or Persian 🇮🇷)
- 💬 Natural conversation flow with GPT-4o
- 🧠 Per-user chat history using SQLite (persists across restarts)
- 📱 Telegram-friendly UX (inline keyboards, typing indicators)
- ♻️ Reset conversation with `/reset`

---

### ⚙️ Requirements

- Python 3.11+
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- An OpenAI API Key

---

### 📁 Project Structure

```
/your-project
├── gpt.py              # Main bot script
├── db.py               # SQLite models & helpers
├── translate.py        # Language strings (EN & FA)
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
└── bot_data/           # SQLite DB stored here
```

---

### 🔧 Setup

1. **Clone the project**

```bash
git clone https://github.com/your-username/telegram-gpt-bot.git
cd telegram-gpt-bot
```

2. **Create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file**

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
WHITELIST_IDS=@yourusername,+49123456789,@anotheruser
```

> ✅ The `WHITELIST_IDS` supports both `@usernames` and `+phone_numbers`.

5. **Run the bot**

```bash
python gpt.py
```

---

### 🧠 Reset Chat History

Users can reset their conversation with:

```
/reset
```

---

### 🛡️ Notes

- The SQLite database is stored in `bot_data/bot_data.db`
- User verification, language preference, and message history are all persisted
- Only whitelisted users can access the bot

---

### 📜 License

MIT — feel free to use, modify, and contribute.
