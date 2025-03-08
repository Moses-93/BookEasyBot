import logging
from aiogram import BaseMiddleware
from aiohttp import ClientResponseError
from aiogram.types import Message, CallbackQuery
from core.constants.error_message import GENERAL_ERROR_MESSAGES, SCHEDULE_ERROR_MESSAGES
from core.exceptions.schedule_exception import ScheduleServiceHTTPError


logger = logging.getLogger(__name__)


async def send_response(event: Message | CallbackQuery, message: str):
    if isinstance(event, CallbackQuery):
        await event.message.answer(text=message)
    elif isinstance(event, Message):
        await event.answer(text=message)


class UserIDMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message | CallbackQuery, data: dict):
        data["user_id"] = event.from_user.id
        return await handler(event, data)


class ErrorHandlingMiddleware(BaseMiddleware):

    async def __call__(self, handler, event: Message | CallbackQuery, data: dict):
        try:
            return await handler(event, data)
        except ScheduleServiceHTTPError as e:
            await self.handle_schedule_error(event, e)
        except ClientResponseError as e:
            await self.handle_client_error(event, e)
        # except Exception as e:
        #     await self.handle_general_error(event, e)

    async def handle_schedule_error(
        self, event: Message | CallbackQuery, error: ScheduleServiceHTTPError
    ):
        logger.info(f"Error: {error}")
        message = SCHEDULE_ERROR_MESSAGES.get(error.status)
        await send_response(event, message)

    async def handle_client_error(
        self, event: Message | CallbackQuery, error: ClientResponseError
    ):
        logger.info(f"Error: {error}")
        message = GENERAL_ERROR_MESSAGES.get(
            error.status, GENERAL_ERROR_MESSAGES["default"]
        )
        await send_response(event, message)

    # async def handle_general_error(
    #     self, event: Message | CallbackQuery, error: Exception
    # ):
    #     logger.info(f"Error: {error}")

    #     await send_response(event, GENERAL_ERROR_MESSAGES["default"])
