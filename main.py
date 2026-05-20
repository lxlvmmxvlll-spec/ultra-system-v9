import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Берем токен из переменных окружения (ВАЖНО для Render)
TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()


# ===== КОМАНДЫ =====

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "🚀 Добро пожаловать в ULTRA SYSTEM v9\n\n"
        "Я помогу тебе прокачать:\n"
        "🧠 мышление\n"
        "🗣 речь\n"
        "⚡ коммуникацию\n\n"
        "Напиши что-нибудь — начнем 👇"
    )


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "📌 Команды:\n"
        "/start — запуск\n"
        "/help — помощь\n\n"
        "Просто пиши сообщения — я буду отвечать."
    )


# ===== ОБРАБОТКА СООБЩЕНИЙ =====

@dp.message()
async def echo_handler(message: types.Message):
    text = message.text

    # Простая логика (можно расширять)
    if "привет" in text.lower():
        await message.answer("Привет 👋 Готов прокачивать тебя")
    elif "задание" in text.lower():
        await message.answer(
            "🔥 Задание дня:\n"
            "Опиши свою цель на 1 год максимально конкретно.\n\n"
            "Не менее 5 предложений."
        )
    else:
        await message.answer(f"Ты написал: {text}")


# ===== ЗАПУСК =====

async def main():
    print("✅ Бот запущен и работает")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
