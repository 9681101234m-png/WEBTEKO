import asyncio
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

TOKEN = "8707687693:AAHCrVyq7s9DW2WQQcrwqVniMtDZj5vUQzg"

CHANNEL_ID = "-1002699431479"

WEBINAR_LINK = "https://teko-com.ru/online-vebinar/vebinar-effektivnaya-sistema-bezopasnosti-s-espe/"

bot = Bot(TOKEN)
dp = Dispatcher()

# --- Web server для Render (чтобы не падал) ---
async def handle(request):
    return web.Response(text="Bot is alive")

async def start_web():
    app = web.Application()
    app.add_routes([web.get("/", handle)])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()


# --- КНОПКИ ---
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подписаться на ТЕКО pro",
                url="https://t.me/teko_pro"
            )
        ],
        [
            InlineKeyboardButton(
                text="Проверить подписку",
                callback_data="check_sub"
            )
        ]
    ]
)

# --- Хэндлер /start ---
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Здравствуйте! Чтобы получить ссылку на вебинар, подпишитесь на канал ТЕКО pro",
        reply_markup=keyboard
    )

# --- Проверка подписки ---
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):

    try:
        member = await bot.get_chat_member(
            CHANNEL_ID,
            callback.from_user.id
        )

        if member.status in ["member", "administrator", "creator"]:
            await callback.message.answer(
                f"Чтобы зарегистрироваться на вебинар, пройдите по ссылке:\n{WEBINAR_LINK}"
            )
        else:
            await callback.message.answer(
                "Вы еще не подписаны на ТЕКО pro."
            )

    except:
        await callback.message.answer(
            "Не удалось проверить подписку. Возможно, бот не админ канала."
        )

    await callback.answer()


# --- ЗАПУСК ---
async def main():
    # ВАЖНО: держим порт для Render
    asyncio.create_task(start_web())

    # запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

