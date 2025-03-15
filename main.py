import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers.user import booking, feedback
from handlers.general import (
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

date_router = handler_factory.create_date_router()
time_router = handler_factory.create_time_router()
service_router = handler_factory.create_service_router()
business_info_router = handler_factory.create_business_info_router()
subscription_router = handler_factory.create_subscription_router()

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
    dp.include_router(date_router.router)
    dp.include_router(time_router.router)
    dp.include_router(business_info_router.router)
    dp.include_router(feedback.router)
    dp.include_router(service_router.router)
    dp.include_router(invite_router.router)
    dp.include_router(time_and_date.router)
    dp.include_router(business_info.router)
    dp.include_router(s.router)
    dp.include_router(subscription_router.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
