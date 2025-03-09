import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers.user import booking, feedback
from handlers.admin import (
    start as admin_start,
    info,
    main as m,
    setting,
    subscription,
)
from handlers.general import (
    booking as b,
    time_and_date,
    business_info,
    service as s,
    user,
)

from core.middleware import UserIDMiddleware, ErrorHandlingMiddleware
from core.dependencies import settings
from handlers.handler_factory import HandlerFactory


BASE_URL = "http://0.0.0.0:8000/api/v1"
API_TOKEN = settings.api_token

handler_factory = HandlerFactory(BASE_URL, API_TOKEN)

admin_date_handler = handler_factory.create_date_admin_handler()
admin_time_handler = handler_factory.create_time_admin_handler()
service_router = handler_factory.service_router()

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
dp.callback_query.middleware(UserIDMiddleware())
dp.message.middleware(ErrorHandlingMiddleware())
dp.callback_query.middleware(ErrorHandlingMiddleware())


async def main():
    dp.include_router(booking.router)
    dp.include_router(user.router)
    dp.include_router(admin_date_handler.router)
    dp.include_router(admin_start.router)
    dp.include_router(admin_time_handler.router)
    dp.include_router(info.router)
    dp.include_router(feedback.router)
    dp.include_router(service_router.router)
    dp.include_router(m.router)
    dp.include_router(b.router)
    dp.include_router(setting.router)
    dp.include_router(time_and_date.router)
    dp.include_router(business_info.router)
    dp.include_router(s.router)
    dp.include_router(subscription.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
