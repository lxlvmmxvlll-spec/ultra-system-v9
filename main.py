import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher()

# ======================
# ULTRA SYSTEM SIMPLE VERSION
# ======================

def generate_day(day: int):
    return f"""
🧠 <b>ULTRA SYSTEM v9</b>

📅 День {day}

🎯 Задача:
Развитие речи и мышления

🎤 Практика:
Объясни свою цель в жизни за 2 минуты

💬 Симуляция:
Убедить собеседника в своей точке зрения

🌍 Миссия:
Начать разговор с человеком

📊 Отчёт:
Напиши результат
"""

user_day = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    user_day[message.from_user.id] = 1
    await message.answer("🧠 ULTRA SYSTEM v9 запущена\nНапиши /day")

@dp.message(Command("day"))
async def day(message: types.Message):
    day_num = user_day.get(message.from_user.id, 1)
    await message.answer(generate_day(day_num))

@dp.message(Command("next"))
async def next_day(message: types.Message):
    uid = message.from_user.id
    user_day[uid] = user_day.get(uid, 1) + 1
    await message.answer(f"➡️ День: {user_day[uid]}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
