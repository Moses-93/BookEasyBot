from aiogram import BaseMiddleware
from aiohttp import ClientResponseError
from aiogram.types import Message, CallbackQuery
from core.constants import ERROR_MESSAGES


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
        except ClientResponseError as e:
            await self.handle_client_error(event, e)
        except Exception as e:
            await self.handle_general_error(event, e)

    async def handle_client_error(self, event: Message | CallbackQuery, error: ClientResponseError):
        message = ERROR_MESSAGES.get(error.status, ERROR_MESSAGES["default"])
        await send_response(event, message)

    async def handle_general_error(self, event: Message | CallbackQuery, error: Exception):
        await send_response(event, ERROR_MESSAGES["default"])