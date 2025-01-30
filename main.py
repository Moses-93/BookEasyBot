import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers.user import user, booking, feedback
from handlers.admin import time, start as admin_start, date, info, admin
from handlers import general
from core.dependencies import settings
from core.middleware import UserIDMiddleware
from handlers.user import user

os.environ["TZ"] = "Europe/Kyiv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


bot = Bot(token=settings.telegram_main_token)
dp = Dispatcher()
dp.message.middleware(UserIDMiddleware())


async def main():
    dp.include_router(general.router)
    dp.include_router(booking.router)
    dp.include_router(user.router)
    dp.include_router(time.router)
    dp.include_router(admin_start.router)
    dp.include_router(date.router)
    dp.include_router(info.router)
    dp.include_router(admin.router)
    dp.include_router(feedback.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
