import logging

from aiogram import Router, F
from aiogram.types import Message

from keyboards.admin import admin_keyboard

from services.api_client import api_client


logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "admin")
async def start(message: Message, user_id: int):
    await api_client.get(endpoint="/users/", chat_id=user_id)

    await message.answer(
        text="Ви перейшли в адмін панель",
        reply_markup=admin_keyboard.admin_main_menu(),
    )
