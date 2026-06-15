import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

# --- ЛОГИ (очень важно для отладки) ---
logging.basicConfig(level=logging.INFO)

# --- ТОКЕН (очень важно для отладки) ---
TOKEN = "8707687693:AAHCrVyq7s9DW2WQQcrwqVniMtDZj5vUQzg"

CHANNEL_ID = "-1002699431479"

WEBINAR_LINK = "https://teko-com.ru/online-vebinar/vebinar-effektivnaya-sistema-bezopasnosti-s-espe/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- WEB SERVER (Render healthcheck) ---
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

# --- /start ---
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Здравствуйте! Чтобы получить ссылку на вебинар, подпишитесь на канал ТЕКО pro 👇",
        reply_markup=keyboard
    )

# --- Проверка подписки ---
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=callback.from_user.id
        )

        if member.status in ("member", "administrator", "creator"):
            await callback.message.answer(
                f"Вот ссылка на вебинар 👇\n{WEBINAR_LINK}"
            )
        else:
            await callback.message.answer(
                "Ты ещё не подписан на канал ТЕКО pro 👀"
            )

    except Exception as e:
        logging.exception("Ошибка проверки подписки:")
        await callback.message.answer(
            "Не удалось проверить подписку. Проверь, добавлен ли бот в канал как админ."
        )

    await callback.answer()

# --- MAIN ---
async def main():
    logging.info("Bot starting...")

    # web server для Render
    asyncio.create_task(start_web())

    # polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
