import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import BOT_TOKEN
from bot.database import init_backup_db, sync_backup
from bot.handlers import start, convert, history, delete

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(convert.router)
    dp.include_router(history.router)
    dp.include_router(delete.router)

    init_backup_db()

    # резервная синхронизация каждую субботу в 00:30 МСК
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(sync_backup,
                      trigger="cron",
                      day_of_week="sat",
                      hour=0,
                      minute=30)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
