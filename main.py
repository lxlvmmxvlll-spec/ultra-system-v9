import asyncio
import logging
import os
import aiosqlite

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "users.db"


# ===== БАЗА ДАННЫХ =====

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1
            )
        """)
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()


async def create_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO users (user_id, username, xp, level) VALUES (?, ?, 0, 1)",
            (user_id, username)
        )
        await db.commit()


async def add_xp(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем текущие данные
        cursor = await db.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()

        xp, level = row
        xp += amount

        # Формула уровня
        new_level = xp // 100 + 1

        await db.execute(
            "UPDATE users SET xp = ?, level = ? WHERE user_id = ?",
            (xp, new_level, user_id)
        )
        await db.commit()

        return xp, level, new_level


# ===== КОМАНДЫ =====

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user = await get_user(message.from_user.id)

    if not user:
        await create_user(message.from_user.id, message.from_user.username)

        await message.answer(
            "🚀 Добро пожаловать в ULTRA SYSTEM v9\n\n"
            "Ты зарегистрирован!\n"
            "Начальный уровень: 1\n"
            "XP: 0\n\n"
            "Пиши сообщения и прокачивайся 💪"
        )
    else:
        await message.answer("Ты уже в системе 💪")


@dp.message(Command("profile"))
async def profile_handler(message: types.Message):
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("Сначала напиши /start")
        return

    user_id, username, xp, level = user

    await message.answer(
        f"👤 Профиль\n\n"
        f"Username: @{username}\n"
        f"Уровень: {level}\n"
        f"XP: {xp}"
    )


# ===== ОСНОВНАЯ ЛОГИКА =====

@dp.message()
async def main_handler(message: types.Message):
    user = await get_user(message.from_user.id)

    if not user:
        await create_user(message.from_user.id, message.from_user.username)

    # Даем XP
    xp, old_level, new_level = await add_xp(message.from_user.id, 10)

    response = ""

    # Проверка уровня
    if new_level > old_level:
        response += f"🎉 Ты повысил уровень!\nТеперь ты {new_level} уровень!\n\n"

    text = message.text.lower()

    if "задание" in text:
        response += (
            "🔥 Задание дня:\n"
            "Опиши свою цель на 1 год.\n"
            "Минимум 5 предложений.\n\n"
            "Ты получишь +20 XP за выполнение (пока вручную 😈)"
        )
    else:
        response += f"💬 Ты написал: {message.text}"

    await message.answer(response)


# ===== ЗАПУСК =====

async def main():
    await init_db()
    print("✅ Бот с системой уровней запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
