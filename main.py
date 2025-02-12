import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers.user import booking, feedback
from handlers.admin import (
    time,
    start as admin_start,
    date,
    info,
    admin,
    service,
    main as m,
    setting,
)
from handlers.general import (
    booking as b,
    time_and_date,
    business_info,
    service as s,
    auth,
)

from core.middleware import UserIDMiddleware, ErrorHandlingMiddleware
from core.dependencies import settings
from core.middleware import UserIDMiddleware

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
    dp.include_router(booking.router)
    dp.include_router(auth.router)
    dp.include_router(time.router)
    dp.include_router(admin_start.router)
    dp.include_router(date.router)
    dp.include_router(info.router)
    dp.include_router(admin.router)
    dp.include_router(feedback.router)
    dp.include_router(service.router)
    dp.include_router(m.router)
    dp.include_router(b.router)
    dp.include_router(setting.router)
    dp.include_router(time_and_date.router)
    dp.include_router(business_info.router)
    dp.include_router(s.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
