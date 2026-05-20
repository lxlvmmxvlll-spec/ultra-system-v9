
import asyncio
import aiosqlite
import os

import asyncio
import aiosqlite
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# ======================
# 🔐 CONFIG
# ======================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()

DB = "ultra.db"

# ======================
# DATABASE
# ======================

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            day INTEGER DEFAULT 1
        )
        """)
        await db.commit()


async def create_user(user_id: int):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        INSERT OR IGNORE INTO users (user_id, day)
        VALUES (?, 1)
        """, (user_id,))
        await db.commit()


async def get_day(user_id: int):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute("""
        SELECT day FROM users WHERE user_id=?
        """, (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 1


async def update_day(user_id: int, day: int):
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        UPDATE users SET day=? WHERE user_id=?
        """, (day, user_id))
        await db.commit()

# ======================
# ULTRA SYSTEM CORE
# ======================

def generate_day(day: int) -> str:
    return f"""
🧠 <b>ULTRA SYSTEM v9</b>

📅 <b>ДЕНЬ {day}</b>

🎯 <b>ЦЕЛЬ:</b>
Развитие речи, мышления и коммуникации

🎤 <b>РЕЧЕВОЕ ЗАДАНИЕ:</b>
Объясни себя за 2 минуты без пауз

🧠 <b>МЫШЛЕНИЕ:</b>
Сформулируй 3 аргумента о своей цели в жизни

💬 <b>СИМУЛЯЦИЯ:</b>
Убедить собеседника в спорной теме

🌍 <b>РЕАЛЬНАЯ МИССИЯ:</b>
Начать разговор с незнакомым человеком

📊 <b>ОТЧЁТ:</b>
Напиши:
- что сделал
- реакция людей
- уверенность (0–10)
"""

# ======================
# HANDLERS
# ======================

@dp.message(Command("start"))
async def start(message: types.Message):
    await create_user(message.from_user.id)
    await message.answer(
        "🧠 ULTRA SYSTEM v9 ACTIVATED\n\nНапиши /day"
    )


@dp.message(Command("day"))
async def day(message: types.Message):
    user_id = message.from_user.id
    d = await get_day(user_id)
    await message.answer(generate_day(d))


@dp.message(Command("next"))
async def next_day(message: types.Message):
    user_id = message.from_user.id
    current = await get_day(user_id)
    new_day = current + 1
    await update_day(user_id, new_day)

    await message.answer(f"➡️ <b>День обновлён:</b> {new_day}")


# ======================
# START APP
# ======================

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
