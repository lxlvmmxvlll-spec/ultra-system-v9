import asyncio
import logging
import aiosqlite
import random
import datetime
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
import threading

from openai import OpenAI

# =========================
# НАСТРОЙКИ
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# FLASK
# =========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =========================
# БАЗА
# =========================
DB_NAME = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            last_mission TEXT
        )
        """)
        await db.commit()

async def create_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
        """, (user_id, username))
        await db.commit()

# =========================
# XP
# =========================
async def add_xp(user_id, amount=10):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET xp = xp + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

        cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
        xp, level = await cursor.fetchone()

        if xp >= level * 100:
            level += 1
            await db.execute("UPDATE users SET level = ?, xp = 0 WHERE user_id = ?", (level, user_id))
            await db.commit()
            return level

    return None

# =========================
# AI КОУЧ
# =========================
def analyze_text(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты AI-коуч по коммуникации.\n"
                        "Анализируй текст пользователя и давай:\n"
                        "1. Краткую оценку\n"
                        "2. Ошибки\n"
                        "3. Как улучшить\n"
                        "4. 1 конкретный совет\n"
                        "Отвечай коротко и по делу."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:
        return "⚠️ Ошибка AI анализа"

# =========================
# ХЕНДЛЕРЫ
# =========================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await create_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "🚀 ULTRA SYSTEM AI\n\n"
        "Теперь я твой AI-коуч.\n"
        "Пиши сообщения — я буду анализировать твою речь 🧠"
    )

@dp.message()
async def main_handler(message: types.Message):
    await create_user(message.from_user.id, message.from_user.username)

    # XP
    new_level = await add_xp(message.from_user.id, 10)

    # AI анализ
    ai_response = analyze_text(message.text)

    reply = f"🧠 Анализ:\n{ai_response}\n\n💬 XP +10"

    if new_level:
        reply += f"\n🎉 Новый уровень: {new_level}!"

    await message.answer(reply)

# =========================
# ЗАПУСК
# =========================
async def main():
    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(main())
