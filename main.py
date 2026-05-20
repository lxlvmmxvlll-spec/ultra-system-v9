import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "ВСТАВЬ_ТОКЕН_ОТ_BOTFATHER"

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB = "ultra.db"


async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            day INTEGER DEFAULT 1
        )
        """)
        await db.commit()


async def create_user(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, day) VALUES (?, 1)",
            (user_id,)
        )
        await db.commit()


async def get_day(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT day FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else 1


async def update_day(user_id, day):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET day=? WHERE user_id=?",
            (day, user_id)
        )
        await db.commit()


def generate_day(day):
    return f"""
🧠 ULTRA SYSTEM v9

📅 ДЕНЬ {day}

🎯 ЦЕЛЬ:
Развитие речи и мышления

🎤 ЗАДАНИЕ:
Объясни себя за 2 минуты

💬 СИМУЛЯЦИЯ:
Убеди собеседника в своей точке зрения

🌍 МИССИЯ:
Начни разговор с человеком

📊 ОТЧЁТ:
Опиши результат
"""


@dp.message(Command("start"))
async def start(message: types.Message):
    await create_user(message.from_user.id)
    await message.answer("🧠 ULTRA SYSTEM v9 запущена\nНапиши /day")


@dp.message(Command("day"))
async def day(message: types.Message):
    d = await get_day(message.from_user.id)
    await message.answer(generate_day(d))


@dp.message(Command("next"))
async def next_day(message: types.Message):
    current = await get_day(message.from_user.id)
    new_day = current + 1
    await update_day(message.from_user.id, new_day)
    await message.answer(f"➡️ День: {new_day}")


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
