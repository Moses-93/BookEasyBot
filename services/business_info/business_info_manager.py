import re
import logging
from typing import Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from keyboards.admin import AdminKeyboard
from states.business_info import CreateBusinessInfoState, UpdateBusinessInfoState
from .business_info_service import BusinessInfoService
from ..user import UserService


MESSAGES = {
    "start": "👋 Вітаємо в панелі керування контактами! Тут ви можете додавати або оновлювати інформацію про вас. Що бажаєте зробити?",
    "add_info": "📝 Давайте почнемо! Як називається ваш салон? Напишіть назву, будь ласка.",
    "edit_info": "🔄 Що саме ви хочете оновити? Оберіть поле зі списку нижче.",
    "address": '📍 Тепер введіть вашу адресу. Наприклад: "м. Одеса, вул. Дерибасівська, 1".',
    "phone_number": "📞 Введіть робочий номер телефону у форматі +380XXXXXXXXX. Наприклад: +380501234567.",
    "invalid_phone": "📵 Ой, схоже, номер телефону введено неправильно: *{phone_number}*.\nБудь ласка, введіть номер у форматі +380XXXXXXXXX. Наприклад: +380501234567. Спробуйте ще раз!",
    "google_link": '🗺️ Додайте посилання на ваш салон у Google Maps, щоб клієнти могли легко вас знайти. Натисніть "Пропустити", якщо не хочете додавати це зараз.',
    "description": '📖 Розкажіть трохи про себе та ваші послуги! Напишіть короткий опис, який зацікавить клієнтів.\nНатисніть "Пропустити", якщо не хочете додавати опис.',
    "telegram_link": '📲 Додайте посилання на ваш Telegram, щоб клієнти могли зв\'язатися з вами через месенджер. Наприклад: "https://t.me/ваш_акаунт". Натисніть "Пропустити", якщо не хочете додавати це зараз.',
    "instagram_link": '📸 Додайте посилання на ваш Instagram, щоб клієнти могли побачити ваші роботи та новини. Наприклад: "https://instagram.com/ваш_акаунт". Натисніть "Пропустити", якщо не хочете додавати це зараз.',
    "info_created": "🎉 Вітаємо! Інформація про ваc успішно збережена. Тепер клієнти зможуть легко знайти вас!",
    "info_updated": '✅ Готово! Поле "*{field}*" успішно оновлено на "*{new_value}*". Клієнти побачать оновлену інформацію.',
    "new_field": '🔄 Введіть нове значення для поля "*{field}*"!',
    "confirm_creation_business_info": "Майже готово. Перевірте вказану інформацію\n\nНазва: *{name}* \nАдреса: *{address}* \nНомер телефону: *{phone_number}* \nОпис: *{description}* \nПосилання Google Maps: *{google_maps_link}* \nПосилання Instagram: *{instagram_link}* \nПосилання Telegram: *{telegram_link}* \n\nЯкщо все правильно - підтвердьте створення контактної інформації!",
}

STATE_MESSAGES = {
    CreateBusinessInfoState.google_link: (MESSAGES["google_link"], "skip_1"),
    CreateBusinessInfoState.description: (MESSAGES["description"], "skip_2"),
    CreateBusinessInfoState.telegram_link: (MESSAGES["telegram_link"], "skip_3"),
    CreateBusinessInfoState.instagram_link: (MESSAGES["instagram_link"], "skip_4"),
}

PHONE_REGEX = r"^\+380\d{9}$"

logger = logging.getLogger(__name__)


class BusinessInfoCreateManager:
    def __init__(self, business_info_service: BusinessInfoService):
        self.business_info_service = business_info_service

    async def send_skip_message(self, state: FSMContext, next_state):
        text, skip_data = STATE_MESSAGES.get(next_state, (None, None))
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="⏭️ Пропустити", callback_data=skip_data)
        await state.set_state(next_state)
        return text, keyboard.as_markup()

    async def handle_skip(self, state: FSMContext, num: str):
        skip_handlers = {
            "1": CreateBusinessInfoState.description,
            "2": CreateBusinessInfoState.telegram_link,
            "3": CreateBusinessInfoState.instagram_link,
            "4": None,
        }
        next_state = skip_handlers.get(num)
        if next_state:
            return await self.send_skip_message(state, next_state)
        elif num == "4":
            data = await state.get_data()
            return await self.confirm_create_business_info(data)

    async def confirm_create_business_info(self, data: Dict[str, str]):
        keyboard = InlineKeyboardBuilder(
            [
                [
                    InlineKeyboardButton(
                        text="✅ Підтвердити",
                        callback_data="confirm_create_business_info",
                    ),
                    InlineKeyboardButton(
                        text="🔄 Редагувати", callback_data="edit_business_info"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Скасувати", callback_data="cancel_create_business_info"
                    ),
                ],
            ]
        )
        message = MESSAGES["confirm_creation_business_info"].format(
            name=data["name"],
            address=data["address"],
            phone_number=data["phone_number"],
            description=data.get("description"),
            google_maps_link=data.get("google_maps_link"),
            instagram_link=data.get("instagram_link"),
            telegram_link=data.get("telegram_link"),
        )
        logger.info(f"Message: {message}")
        return message, keyboard.as_markup()

    async def start_add_info(self, state: FSMContext):
        await state.set_state(CreateBusinessInfoState.name)
        return MESSAGES["add_info"]

    async def set_name(self, state: FSMContext, name: str):
        await state.update_data(name=name)
        await state.set_state(CreateBusinessInfoState.address)
        return MESSAGES["address"]

    async def set_address(self, state: FSMContext, address: str):
        await state.update_data(address=address)
        await state.set_state(CreateBusinessInfoState.phone_number)
        return MESSAGES["phone_number"]

    async def set_phone_number(self, state: FSMContext, phone_number: str):
        if not re.match(PHONE_REGEX, phone_number):
            return MESSAGES["invalid_phone"].format(phone_number=phone_number), None
        await state.update_data(phone_number=phone_number)
        return await self.send_skip_message(state, CreateBusinessInfoState.description)

    async def set_description(self, state: FSMContext, description: str):
        await state.update_data(description=description)
        return await self.send_skip_message(state, CreateBusinessInfoState.google_link)

    async def set_google_link(self, state: FSMContext, google_link: str):
        await state.update_data(google_maps_link=google_link)
        return await self.send_skip_message(
            state, CreateBusinessInfoState.telegram_link
        )

    async def set_telegram_link(self, state: FSMContext, telegram_link):
        await state.update_data(telegram_link=telegram_link)
        return await self.send_skip_message(
            state, CreateBusinessInfoState.instagram_link
        )

    async def set_instagram_link(self, state: FSMContext, instagram_link: str):
        await state.update_data(instagram_link=instagram_link)
        data = await state.get_data()
        logger.info(f"Business-data: {data}")
        return await self.confirm_create_business_info(data)

    async def finish_create_business_info(self, state: FSMContext, user_id: int):
        data = await state.get_data()
        created_business_info = await self.business_info_service.create_business_info(
            user_id, data
        )
        await state.clear()
        return MESSAGES["info_created"]


class BusinessInfoUpdateManager:

    def __init__(self, business_info_service: BusinessInfoService):
        self.business_info_service = business_info_service

    async def start_edit_info(self, state: FSMContext):
        keyboard = InlineKeyboardBuilder(
            [
                [
                    InlineKeyboardButton(text="Назва", callback_data="name"),
                    InlineKeyboardButton(text="Адреса", callback_data="address"),
                    InlineKeyboardButton(
                        text="Номер телефону", callback_data="phone_number"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Номер телефону", callback_data="phone_number"
                    ),
                    InlineKeyboardButton(text="Опис", callback_data="description"),
                ],
                [
                    InlineKeyboardButton(
                        text="Google Maps", callback_data="google_maps_link"
                    ),
                    InlineKeyboardButton(
                        text="Instagram", callback_data="instagram_link"
                    ),
                    InlineKeyboardButton(
                        text="Telegram", callback_data="telegram_link"
                    ),
                ],
            ]
        )
        await state.set_state(UpdateBusinessInfoState.field)
        return MESSAGES["edit_info"], keyboard.as_markup()

    async def start_update_field(self, state: FSMContext, field: str):
        await state.update_data(field=field)
        await state.set_state(UpdateBusinessInfoState.new_value)
        return MESSAGES["new_field"].format(field=field)

    async def update_field_value(self, state: FSMContext, new_value: str, user_id: int):
        field = await state.get_value("field")
        logger.info(f"field: {field}")
        await self.business_info_service.update_business_info(
            user_id, {field: new_value}
        )
        await state.clear()
        return MESSAGES["info_updated"].format(field=field, new_value=new_value)


class BusinessInfoManager:

    def __init__(
        self,
        creation_manager: BusinessInfoCreateManager,
        update_manager: BusinessInfoUpdateManager,
        business_info_service: BusinessInfoService,
        user_service: UserService,
        admin_keyboard: AdminKeyboard,
    ):
        self.business_info_service = business_info_service
        self.user_service = user_service
        self.admin_keyboard = admin_keyboard
        self.creation_manager = creation_manager
        self.update_manager = update_manager

    async def start(self, user_id):
        await self.user_service.get_user(user_id)
        return MESSAGES["start"], self.admin_keyboard.manage_contacts()
