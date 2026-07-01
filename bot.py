import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import random

# ============================
# ВСТАВЬ СВОЙ ТОКЕН СЮДА
TOKEN = "8855453766:AAGxp9Snp9JSPAeDplgTu9nFSIte7BBXXfg"
# URL твоего Mini App на Netlify
WEBAPP_URL = "https://extraordinary-dasik-ac6b15.netlify.app/"
# ============================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище подписчиков (в памяти — для продакшена используй БД)
subscribers = set()

REMINDERS = [
    "Что ты сейчас чувствуешь? Назови это.",
    "Остановись на секунду. Что внутри?",
    "Момент присутствия. Что происходит в теле?",
    "Есть ли напряжение? Или покой?",
    "Назови одним словом своё состояние прямо сейчас.",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribers.add(user_id)
    name = update.effective_user.first_name or "друг"

    keyboard = [[InlineKeyboardButton(
        "Открыть приложение",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Привет, {name} 👋\n\n"
        f"*Эффект присутствия. Начало* — практика осознанности и дисциплины.\n\n"
        f"Я буду напоминать тебе несколько раз в день:\n"
        f"_«Что ты сейчас чувствуешь?»_\n\n"
        f"Уведомления приходят с 8:00 до 22:00.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribers.discard(user_id)
    await update.message.reply_text("Уведомления отключены. Напиши /start чтобы включить снова.")

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "Открыть приложение",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Открываю:", reply_markup=reply_markup)

async def send_reminders(app):
    if not subscribers:
        return
    text = random.choice(REMINDERS)
    keyboard = [[InlineKeyboardButton(
        "Зафиксировать",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for user_id in list(subscribers):
        try:
            await app.bot.send_message(
                chat_id=user_id,
                text=f"🔔 {text}",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить {user_id}: {e}")
            subscribers.discard(user_id)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("app", open_app))

    scheduler = AsyncIOScheduler()

    # Каждые ~90 минут с 8 до 22, случайная минута для разнообразия
    for hour in [8, 9, 11, 13, 15, 17, 19, 21]:
        minute = random.randint(0, 30)
        scheduler.add_job(
            send_reminders,
            CronTrigger(hour=hour, minute=minute),
            args=[app]
        )

    scheduler.start()
    logger.info("Бот запущен. Подписчики будут получать уведомления с 8 до 22.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

