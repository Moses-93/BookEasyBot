import logging

from aiogram import Router, F
from aiogram.types import Message

from keyboards.admin import reply_keyboard


logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "admin")
async def start(message: Message):
    await message.answer(
        text="Ви перейшли в адмін панель",
        reply_markup=reply_keyboard.admin_main_menu(),
    )
