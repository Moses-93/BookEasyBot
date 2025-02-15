import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, BaseFilter
from aiogram.fsm.context import FSMContext
from aiohttp import ClientResponseError

from keyboards.general import dynamic_keyboard
from keyboards.factory_method import IdentifyRole
from services.api_client import api_client
from states.auth import AuthState
from utils import validation as val


logger = logging.getLogger(__name__)

router = Router()

MESSAGE = {
    "info": "Привіт! Цей бот - перевірене рішення для індивідуальних майстрів та салонів Beauty сфери, яке призначене для заощадження часу, ведення обліку та спрощення комунікації з клієнтами",
    "master": "Привіт {name}! Радий знову тебе бачити.\nПочнімо працювати?!",
    "user": "Радий вас знову бачити, {name}!\nЧим можу бути корисним?",
    "sign_up": "Чудовий вибір, ви на шляху до успіху!\nДля реєстрації нам всього лиш потрібен ваш номер телефону. Не хвилюйтеся, ми відповідаємо всім вимогам законодавства, тому використовуємо кодування особистої інформації!",
    "successful_register_master": "{name}, це успіх! Ознайомтесь з форматами підписки в розділі налаштувань та поспішайте працювати.\nУспіхів Вам!",
    "successful_register_user": "Чудово! {name}, ви успішно пройшли реєстрацію, та вже можете записатись до вашого майстра!",
}


class DeepLinkFilter(BaseFilter):
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, message: Message) -> bool:
        if not message.text or not message.text.startswith("/start"):
            return False

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return False

        deep_link_param = parts[1]
        return deep_link_param.startswith(self.prefix)


async def process_sign_up(
    message: Message,
    state: FSMContext,
    user_id: int,
    master_id: int = None,
    role: str = "client",
):
    """Обробляє реєстрацію для користувача або майстра."""
    await state.update_data(
        name=message.from_user.full_name,
        username=message.from_user.username,
        role=role,
        master_id=master_id,
        chat_id=user_id,
    )

    contact_button = KeyboardButton(text="📞 Поділитися номером", request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[contact_button]], resize_keyboard=True)

    await message.answer(
        text=MESSAGE["sign_up"],
        reply_markup=keyboard,
    )
    await state.set_state(AuthState.phone_number)


@router.message(CommandStart(deep_link=True), DeepLinkFilter(prefix="master"))
async def start_sign_up(message: Message, state: FSMContext, user_id: int):
    deep_link_param = message.text.split(maxsplit=1)[1]

    try:
        master_id = int(deep_link_param[len("master") :])
        logger.info(f"master-id: {master_id}")
    except (IndexError, ValueError):
        await message.answer("Посилання має некоректний формат!")
        return

    await process_sign_up(message, state, user_id, master_id)


@router.message(CommandStart())
async def start(message: Message, user_id: int):
    try:
        status, user = await api_client.get(endpoint="/users/", chat_id=user_id)
    except ClientResponseError as e:
        if e.status == 401:
            await message.answer(
                text=MESSAGE["info"],
                reply_markup=dynamic_keyboard.dynamic_reply_keyboard(
                    ["✅ Стати майстром"]
                ),
            )
            return
    await message.answer(
        text=MESSAGE[user["role"]].format(name=user["name"]),
        reply_markup=IdentifyRole.generate_keyboard(user["role"]),
    )


router.message(F.text == "✅ Стати майстром")


async def to_be_master(message: Message, state: FSMContext, user_id: int):
    await state.set_state(AuthState.phone_number)

    await process_sign_up(message, state, "master", user_id)


@router.message(AuthState.phone_number)
async def finish_sign_up(message: Message, state: FSMContext, user_id: int):
    phone_number = message.contact.phone_number
    logger.info(f"Phone_number:{phone_number}")

    await state.update_data(phone=phone_number)
    data = await state.get_data()
    status, user = await api_client.post(f"/users/", chat_id=user_id, json=data)
    if status == 201:
        await message.answer(
            text=MESSAGE[f"successful_register_{user["role"]}"].format(
                name=user["name"]
            ),
            reply_markup=IdentifyRole.generate_keyboard(user["role"]),
        )
