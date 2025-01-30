import re
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.api_client import api_client
from states.business_info import *
from keyboards.admin import reply_keyboard
from keyboards.general import dynamic_keyboard


PHONE_REGEX = r"^\+380\d{9}$"
router = Router()
logger = logging.getLogger(__name__)


MESSAGES = {
    "start": "👋 Вітаємо в панелі керування контактами! Тут ви можете додавати або оновлювати інформацію про ваш салон. Що бажаєте зробити?",
    "add_info": "📝 Давайте почнемо! Як називається ваш салон? Напишіть назву, будь ласка.",
    "edit_info": "🔄 Що саме ви хочете оновити? Оберіть поле зі списку нижче.",
    "address": '📍 Тепер введіть адресу вашого салону. Наприклад: "м. Одеса, вул. Дерибасівська, 1". Де знаходиться ваш салон?',
    "phone": "📞 Введіть номер телефону вашого салону у форматі +380XXXXXXXXX. Наприклад: +380501234567. Як клієнти можуть з вами зв'язатися?",
    "invalid_phone": "📵 Ой, схоже, номер телефону введено неправильно. Будь ласка, введіть номер у форматі +380XXXXXXXXX. Наприклад: +380501234567. Спробуйте ще раз!",
    "working_hours": '⏰ Вкажіть графік роботи вашого салону у форматі HH:MM-HH:MM. Наприклад: "9:00-18:00". Коли ви працюєте?',
    "google_link": '🗺️ Додайте посилання на ваш салон у Google Maps, щоб клієнти могли легко вас знайти. Натисніть "Пропустити", якщо не хочете додавати це зараз.',
    "description": '📖 Розкажіть трохи про ваш салон! Напишіть короткий опис, який зацікавить клієнтів. Наприклад: "Сучасний салон краси з професійними майстрами". Натисніть "Пропустити", якщо не хочете додавати опис.',
    "telegram_link": '📲 Додайте посилання на ваш Telegram, щоб клієнти могли зв\'язатися з вами через месенджер. Наприклад: "https://t.me/ваш_акаунт". Натисніть "Пропустити", якщо не хочете додавати це зараз.',
    "instagram_link": '📸 Додайте посилання на ваш Instagram, щоб клієнти могли побачити ваші роботи та новини. Наприклад: "https://instagram.com/ваш_акаунт". Натисніть "Пропустити", якщо не хочете додавати це зараз.',
    "info_created": "🎉 Вітаємо! Інформація про ваш салон успішно збережена. Тепер клієнти зможуть легко знайти вас!",
    "info_updated": '✅ Готово! Поле "{field}" успішно оновлено на "{new_value}". Клієнти побачать оновлену інформацію.',
    "new_field": '🔄 Введіть нове значення для поля "{field}". Наприклад, якщо це "Назва", напишіть нову назву вашого салону. Що ви хочете ввести?',
    "update_error": '❌ Упс! Не вдалося оновити поле "{field}". Перевірте, чи правильно ви ввели дані, і спробуйте ще раз.',
    "api_error": "😕 Упс! Щось пішло не так. Помилка: {error}. Спробуйте ще раз або зверніться до підтримки.",
}

STATE_MESSAGES = {
    CreateBusinessInfoState.google_link: (MESSAGES["google_link"], "skip_1"),
    CreateBusinessInfoState.description: (MESSAGES["description"], "skip_2"),
    CreateBusinessInfoState.telegram_link: (MESSAGES["telegram_link"], "skip_3"),
    CreateBusinessInfoState.instagram_link: (MESSAGES["instagram_link"], "skip_4"),
}


async def send_skip_message(message: Message, state: FSMContext, next_state):
    text, skip_data = STATE_MESSAGES.get(next_state, (None, None))
    if text:
        await message.answer(
            text=text,
            reply_markup=dynamic_keyboard.dynamic_inline_keyboard(
                {"⏭️ Пропустити": skip_data}
            ),
        )
        await state.set_state(next_state)


@router.message(F.text == "Керувати контактами")
async def start(message: Message):
    await message.answer(
        text=MESSAGES["start"], reply_markup=reply_keyboard.manage_contacts()
    )


@router.message(F.text == "Додати інформацію")
async def start_add_info(message: Message, state: FSMContext):
    await message.answer(text=MESSAGES["add_info"])
    await state.set_state(CreateBusinessInfoState.name)


@router.message(F.text == "Оновити інформацію")
async def start_edit_info(message: Message, state: FSMContext):
    keyboard = dynamic_keyboard.dynamic_inline_keyboard(
        {
            "Назва": "name",
            "Адреса": "address",
            "Номер телефону": "phone",
            "Графік роботи": "working_hours",
            "Опис": "description",
            "Google Maps": "google_maps_link",
            "Instagram": "instagram_link",
            "Telegram": "telegram_link",
        }
    )
    await message.answer(text=MESSAGES["edit_info"], reply_markup=keyboard)
    await state.set_state(UpdateBusinessInfoState.field)


@router.message(CreateBusinessInfoState.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text=MESSAGES["address"])
    await state.set_state(CreateBusinessInfoState.address)


@router.message(CreateBusinessInfoState.address)
async def set_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer(text=MESSAGES["phone"])
    await state.set_state(CreateBusinessInfoState.phone)


@router.message(CreateBusinessInfoState.phone)
async def set_phone(message: Message, state: FSMContext):
    if not re.match(PHONE_REGEX, message.text):
        await message.answer(MESSAGES["invalid_phone"])
        return
    await state.update_data(phone=message.text)
    await message.answer(text=MESSAGES["working_hours"])
    await state.set_state(CreateBusinessInfoState.working_hours)


@router.message(CreateBusinessInfoState.working_hours)
async def set_working_hours(message: Message, state: FSMContext):
    await state.update_data(working_hours=message.text)
    await send_skip_message(message, state, CreateBusinessInfoState.google_link)


@router.message(CreateBusinessInfoState.google_link)
async def set_google_link(message: Message, state: FSMContext):
    await state.update_data(google_maps_link=message.text)
    await send_skip_message(message, state, CreateBusinessInfoState.description)


@router.message(CreateBusinessInfoState.description)
async def set_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await send_skip_message(message, state, CreateBusinessInfoState.telegram_link)


@router.message(CreateBusinessInfoState.telegram_link)
async def set_telegram_link(message: Message, state: FSMContext):
    await state.update_data(telegram_link=message.text)
    await send_skip_message(message, state, CreateBusinessInfoState.instagram_link)


@router.message(CreateBusinessInfoState.instagram_link)
async def set_instagram_link(message: Message, state: FSMContext):
    await state.update_data(instagram_link=message.text)
    data = await state.get_data()
    status, msg = await api_client.post(
        endpoint="/business-info/", chat_id=message.from_user.id, json=data
    )
    if status == 201:
        await message.answer(MESSAGES["info_created"])
    else:
        await message.answer(text=MESSAGES["api_error"].format(error=str(msg)))
    await state.clear()


@router.callback_query(F.data.startswith("skip_"))
async def handle_skip(callback: CallbackQuery, state: FSMContext):
    num = callback.data.split("_")[1]
    skip_handlers = {
        "1": CreateBusinessInfoState.description,
        "2": CreateBusinessInfoState.telegram_link,
        "3": CreateBusinessInfoState.instagram_link,
        "4": None,
    }
    next_state = skip_handlers.get(num)
    if next_state:
        await send_skip_message(callback.message, state, next_state)
    elif num == "4":
        data = await state.get_data()
        status, msg = await api_client.post(
            endpoint="/business-info/", chat_id=callback.from_user.id, json=data
        )
        if status == 201:
            await callback.message.answer(MESSAGES["info_created"])
        else:
            await callback.message.answer(
                text=MESSAGES["api_error"].format(error=str(msg))
            )
        await state.clear()
    await callback.answer()


@router.callback_query(UpdateBusinessInfoState.field)
async def start_update_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data
    await state.update_data(field=field)
    await callback.message.answer(text=MESSAGES["new_field"].format(field=field))
    await state.set_state(UpdateBusinessInfoState.new_value)
    await callback.answer()


@router.message(UpdateBusinessInfoState.new_value)
async def update_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    new_value = message.text
    try:
        status, msg = await api_client.patch(
            endpoint=f"/business-info/{field}/",
            chat_id=message.from_user.id,
            json={field: new_value},
        )
        if status == 204:
            await message.answer(
                text=MESSAGES["info_updated"].format(field=field, new_value=new_value)
            )
        elif status == 422:
            await message.answer(text=MESSAGES["update_error"].format(field=field))
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(text=MESSAGES["api_error"].format(error=str(e)))
    await state.clear()
