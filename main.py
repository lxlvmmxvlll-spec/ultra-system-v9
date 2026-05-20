import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from flask import Flask
import threading

# ====== НАСТРОЙКИ ======
TOKEN = os.getenv("BOT_TOKEN")  # токен из Render

# ====== ЛОГИ ======
logging.basicConfig(level=logging.INFO)

# ====== БОТ ======
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== КОМАНДЫ ======
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚀 Бот запущен и работает!")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

# ====== FLASK (для Render) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ====== ЗАПУСК ======
async def main():
    # ❗ фикс конфликта
    await bot.delete_webhook(drop_pending_updates=True)

    # запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    # запускаем веб-сервер
    threading.Thread(target=run_web).start()

    # запускаем бота
    asyncio.run(main())
