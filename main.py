import asyncio
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

# === НАСТРОЙКИ ===
TOKEN = "8707687693:AAHCrVyq7s9DW2WQQcrwqVniMtDZj5vUQzg"
CHANNEL_ID = "-1002699431479"
WEBINAR_LINK = "https://teko-com.ru/online-vebinar/vebinar-effektivnaya-sistema-bezopasnosti-s-espe/"

# Для Render
PORT = int(os.getenv("PORT", 10000)) # Render даёт свой порт
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'your-app.onrender.com')}{WEBHOOK_PATH}"

bot = Bot(TOKEN)
dp = Dispatcher()

# ================== КНОПКИ ==================
keyboard = InlineKeyboardMarkup(
inline_keyboard=[
[InlineKeyboardButton(text="Подписаться на ТЕКО pro", url="https://t.me/teko_pro")],
[InlineKeyboardButton(text="Проверить подписку", callback_data="check_sub")]
]
)

# ================== ХЭНДЛЕРЫ ==================
@dp.message(CommandStart())
async def start(message: Message):
await message.answer(
"Здравствуйте! Чтобы получить ссылку на вебинар, подпишитесь на канал ТЕКО pro",
reply_markup=keyboard
)

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
try:
member = await bot.get_chat_member(CHANNEL_ID, callback.from_user.id)

if member.status in ["member", "administrator", "creator"]:
await callback.message.answer(
f"Чтобы зарегистрироваться на вебинар, пройдите по ссылке:\n{WEBINAR_LINK}"
)
else:
await callback.message.answer("Вы еще не подписаны на ТЕКО pro.")

except Exception as e:
await callback.message.answer("Не удалось проверить подписку. Попробуйте позже.")
print(f"Error checking subscription: {e}") # для логов

await callback.answer()

# ================== WEBHOOK ==================
async def on_startup(app):
await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
print(f"✅ Webhook успешно установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
await bot.session.close()
print("⛔ Бот остановлен")

# Основной веб-сервер
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Регистрируем обработчик вебхука
webhook_handler = web.RequestHandler(dispatcher=dp, bot=bot) # aiogram 3.x
app.router.add_post(WEBHOOK_PATH, webhook_handler)

# Простая страница, чтобы Render видел, что сервис живой
async def handle_root(request):
return web.Response(text="Bot is running with webhook ✅")

app.router.add_get("/", handle_root)

# ================== ЗАПУСК ==================
if __name__ == "__main__":
print("🚀 Запуск бота с webhook...")
web.run_app(app, host="0.0.0.0", port=PORT)
