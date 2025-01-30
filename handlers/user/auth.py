import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.general import general_reply_keyboard
from services.api_client import api_client

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    """Обробляє команду /start та перевіряє наявність майстра"""
    start_data = (
        message.text.split(" ", maxsplit=1)[1]
        if len(message.text.split()) > 1
        else None
    )
    user_id = message.from_user.id

    # Якщо користувач зайшов без посилання майстра
    if not start_data or not start_data.startswith("master_"):
        await message.answer(
            "Для використання цього бота вам потрібно отримати посилання від вашого майстра."
        )
        return

    # Отримуємо master_id
    try:
        master_id = int(start_data.split("_")[1])
    except ValueError:
        await message.answer(
            "Посилання має некоректний формат! Перевірте його та спробуйте ще раз."
        )
        return

    # Реєструємо користувача
    name = message.from_user.first_name
    username = message.from_user.username

    status, msg = await api_client.post(
        endpoint="/users/sign-up",
        chat_id=user_id,
        json={
            "name": name,
            "username": username,
            "master_id": master_id,
            "chat_id": user_id,
            "role": "user",
        },
    )

    if status == 201:
        await message.answer(
            "Ви успішно зареєстровані!",
            reply_markup=general_reply_keyboard.main_keyboard(),
        )
    elif status == 409:
        await message.answer(
            "Ви вже зареєстровані!", reply_markup=general_reply_keyboard.main_keyboard()
        )
    else:
        await message.answer(
            "Помилка реєстрації. Спробуйте ще раз або зверніться до адміністратора."
        )
