import os
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
Message,
CallbackQuery,
InlineKeyboardMarkup,
InlineKeyboardButton
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# === НАСТРОЙКИ ===
TOKEN = "8707687693:AAHCrVyq7s9DW2WQQcrwqVniMtDZj5vUQzg"
CHANNEL_ID = "-1002699431479"

WEBINAR_LINK = (
"https://teko-com.ru/online-vebinar/"
"vebinar-effektivnaya-sistema-bezopasnosti-s-espe/"
)

PORT = int(os.getenv("PORT", 10000))
WEBHOOK_PATH = "/webhook"

WEBHOOK_URL = (
f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
f"{WEBHOOK_PATH}"
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================== КНОПКИ ==================

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

# ================== ХЭНДЛЕРЫ ==================

@dp.message(CommandStart())
async def start(message: Message):
await message.answer(
"Здравствуйте! Чтобы получить ссылку на вебинар, "
"подпишитесь на канал ТЕКО pro",
reply_markup=keyboard
)


@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
try:
member = await bot.get_chat_member(
CHANNEL_ID,
callback.from_user.id
)

if member.status in ["member", "administrator", "creator"]:
await callback.message.answer(
f"✅ Чтобы зарегистрироваться на вебинар, "
f"пройдите по ссылке:\n\n{WEBINAR_LINK}"
)
else:
await callback.message.answer(
"Вы ещё не подписаны на ТЕКО pro."
)

except Exception as e:
print(f"Ошибка проверки подписки: {e}")

await callback.message.answer(
"Не удалось проверить подписку. Попробуйте позже."
)

await callback.answer()

# ================== WEBHOOK ==================

async def on_startup(app: web.Application):
await bot.set_webhook(
WEBHOOK_URL,
drop_pending_updates=True
)

print(f"Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(app: web.Application):
await bot.session.close()
print("Бот остановлен")


# ================== ЗАПУСК ==================

async def handle_root(request):
return web.Response(
text="Bot is running with webhook"
)


if __name__ == "__main__":
app = web.Application()

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

app.router.add_get("/", handle_root)

SimpleRequestHandler(
dispatcher=dp,
bot=bot
).register(
app,
path=WEBHOOK_PATH
)

print("Запуск бота...")

web.run_app(
app,
host="0.0.0.0",
port=PORT
)
