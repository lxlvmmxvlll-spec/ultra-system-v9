import asyncio
import logging
import aiosqlite

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
import threading
import os

# =========================
# НАСТРОЙКИ
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# FLASK (для Render)
# =========================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =========================
# БАЗА ДАННЫХ
# =========================
DB_NAME = "users.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0
        )
        """)
        await db.commit()

# 🔥 ФИКС ЗДЕСЬ
async def create_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (user_id, username)
        VALUES (?, ?)
        """, (user_id, username))
        await db.commit()

async def add_xp(user_id, amount=10):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        UPDATE users SET xp = xp + ?
        WHERE user_id = ?
        """, (amount, user_id))
        await db.commit()

        # проверка уровня
        cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        xp, level = row

        if xp >= level * 100:
            level += 1
            await db.execute("""
            UPDATE users SET level = ?, xp = 0
            WHERE user_id = ?
            """, (level, user_id))
            await db.commit()
            return level

    return None

async def get_profile(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT level, xp FROM users WHERE user_id = ?
        """, (user_id,))
        return await cursor.fetchone()

# =========================
# ХЕНДЛЕРЫ
# =========================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await create_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "🚀 Добро пожаловать в ULTRA SYSTEM\n\n"
        "Ты начал путь развития.\n"
        "Пиши любое сообщение, чтобы получать XP 🔥"
    )

@dp.message(Command("profile"))
async def profile_handler(message: types.Message):
    data = await get_profile(message.from_user.id)

    if data:
        level, xp = data
        await message.answer(f"👤 Уровень: {level}\n🔥 XP: {xp}/100")

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
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(main())
