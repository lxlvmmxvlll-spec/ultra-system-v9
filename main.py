import asyncio
import logging
import aiosqlite
import random
import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
import threading
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

DB_NAME = "users.db"

# =========================
# БАЗА
# =========================
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
# XP / УРОВНИ
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

async def get_profile(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT level, xp FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

# =========================
# МИССИИ
# =========================
MISSIONS = [
    "Скажи комплимент незнакомому человеку",
    "Задай 3 глубоких вопроса в разговоре",
    "Расскажи историю на 1 минуту",
    "Вырази свою точку зрения уверенно",
    "Поговори с новым человеком"
]

async def get_mission(user_id):
    today = str(datetime.date.today())

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT last_mission FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        if row and row[0] == today:
            return None  # уже была миссия сегодня

        mission = random.choice(MISSIONS)

        await db.execute("UPDATE users SET last_mission = ? WHERE user_id = ?", (today, user_id))
        await db.commit()

        return mission

# =========================
# ХЕНДЛЕРЫ
# =========================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await create_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "🚀 ULTRA SYSTEM v1\n\n"
        "Ты начинаешь прокачку коммуникации.\n"
        "Пиши сообщения → получаешь XP 🔥\n\n"
        "/mission — задание дня\n"
        "/profile — твой уровень"
    )

@dp.message(Command("profile"))
async def profile_handler(message: types.Message):
    data = await get_profile(message.from_user.id)

    if data:
        level, xp = data
        await message.answer(f"👤 Уровень: {level}\n🔥 XP: {xp}/{level*100}")

@dp.message(Command("mission"))
async def mission_handler(message: types.Message):
    mission = await get_mission(message.from_user.id)

    if mission:
        await message.answer(f"🎯 Твоя миссия на сегодня:\n\n{mission}\n\n+50 XP за выполнение")
    else:
        await message.answer("✅ Ты уже получил миссию сегодня")

@dp.message()
async def main_handler(message: types.Message):
    await create_user(message.from_user.id, message.from_user.username)

    new_level = await add_xp(message.from_user.id, 10)

    if new_level:
        await message.answer(f"🎉 Новый уровень: {new_level}!")

    await message.answer("💬 XP +10")

# =========================
# ЗАПУСК
# =========================
async def main():
    await init_db()

    # фикс конфликтов
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(main())
