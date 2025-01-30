import re
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.api_client import api_client
from states.business_info import *
from keyboards.admin import inline_keyboard, reply_keyboard
from keyboards.general import dynamic_keyboard

PHONE_REGEX = r"^\+380\d{9}$"
router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "Керувати контактами")
async def start(message: Message):
    await message.answer(
        text="Ви перейли в панель керування контактами! \nОберіть потрібну вам дію!",
        reply_markup=reply_keyboard.manage_contacts(),
    )
    return


@router.message(F.text == "Додати інформацію")
async def start_add_info(message: Message, state: FSMContext):
    await message.answer(text="Введіть назву вашого салону!")
    await state.set_state(CreateBusinessInfoState.name)
    return


@router.message(F.text == "Оновити інформацію")
async def start_edit_info(message: Message, state: FSMContext):
    keyboard = dynamic_keyboard.dynamic_inline_keyboard(
        {
            "Назва": "name",
            "Адреса": "address",
            "Номер телефону": "phone",
            "Графік роботи": "working_hours",
            "Опис": "description",
            "Google Maps": "google_maps_url",
        }
    )
    await message.answer(
        text="Оберіть поле, яке ви хочете оновити!", reply_markup=keyboard
    )
    await state.set_state(UpdateBusinessInfoState.field)


@router.message(CreateBusinessInfoState.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="Введіть адресу вашого салону!\nПриклад: м. Одеса вул. Дерибасівська 1"
    )
    await state.set_state(CreateBusinessInfoState.address)
    return


@router.message(CreateBusinessInfoState.address)
async def set_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer(
        text="Введіть ваш робочий номер телефону!\nПриклад: +380501234567"
    )
    await state.set_state(CreateBusinessInfoState.phone)
    return


@router.message(CreateBusinessInfoState.phone)
async def set_phone(message: Message, state: FSMContext):
    if not re.match(PHONE_REGEX, message.text):
        await message.answer("Неправильний формат телефону! Спробуйте знову.")
        return
    await state.update_data(phone=message.text)
    await message.answer(
        text="Введіть ваш графік роботи у форматі HH:MM!\nПриклад: 9:00-18:00"
    )
    await state.set_state(CreateBusinessInfoState.working_hours)


@router.message(CreateBusinessInfoState.working_hours)
async def set_working_hours(message: Message, state: FSMContext):
    await state.update_data(working_hours=message.text)
    await message.answer(
        text="Вказаної вами інформації вже достатньо!\nЗа бажанням ви можете додати додатковий опис або посилання в Google Maps на місцезнаходження вашого салону!\nЯкщо вам достатньо вже вказаної інформації - натисність відповідну кнопку",
        reply_markup=inline_keyboard.description_or_google_link_or_confirm(),
    )
    return


@router.callback_query(F.data == "add_description")
async def start_set_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Введіть додатковий опис вашого салону!")
    await state.set_state(CreateBusinessInfoState.description)
    return


@router.callback_query(F.data == "add_google_link")
async def set_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="Введіть посилання в Google Maps місцезнаходження вашого салону!"
    )
    await state.set_state(CreateBusinessInfoState.google_link)
    return


@router.callback_query(F.data == "confirm")
async def create_info(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        response = await api_client.post(
            endpoint="/business-info/", chat_id=callback.from_user.id, json=data
        )
        if response.status == 201:
            await callback.message.answer(text="Контактна інформація успішно додана!")
            await state.clear()
            return
    except Exception as e:
        logger.error(f"Error: {e}")
        await callback.message.answer(f"Помилка при збереженні даних: {str(e)}")
        await state.clear()
    return


@router.message(CreateBusinessInfoState.description)
async def set_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    if not data.get("google_link"):
        await message.answer(
            text="Опис прийнято! Завершіть додавання даних або додайте посилання Google Maps!",
            reply_markup=dynamic_keyboard.dynamic_reply_keyboard({"Додати посилання Google Maps":"add_google_link", "Підтвердити":"confirm"})
        )
        await state.set_state(CreateBusinessInfoState.google_link)
        return
    await message.answer(
        text="Ви успішно додали контактні дані!"
    )  # TODO: інітація запиту до бекенду
    return


@router.message(CreateBusinessInfoState.google_link)
async def set_link(message: Message, state: FSMContext):
    await state.update_data(google_link=message.text)
    data = await state.get_data()
    if not data.get("description"):
        await message.answer(
            text="Посилання прийнято!\nЗавершіть додавання даних або додайте опис!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Додати опис",
                            callback_data="add_description",
                        )
                    ],
                    [InlineKeyboardButton(text="Завершити", callback_data="confirm")],
                ]
            ),
        )
        await state.set_state(CreateBusinessInfoState.description)
        return
    await message.answer(text="Ви успішно додали контактні дані!")
    await state.clear()
    return


@router.callback_query(UpdateBusinessInfoState.field)
async def start_update_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data
    await state.update_data(field=field)
    await callback.message.answer(text=f"Введть нове значення поля {field}")
    await state.set_state(UpdateBusinessInfoState.new_value)
    await callback.answer()


@router.message(UpdateBusinessInfoState.new_value)
async def update_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("field")
    new_value = message.text
    try:
        response = await api_client.patch(
            endpoint=f"/business-info/{field}/",
            chat_id=message.from_user.id,
            json={field: new_value},
        )
        if response.status == 200:
            await message.answer(text=f"Значення поля {field} успішно оновлено!")
            await state.clear()
            return
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer(f"Помилка при оновленні значення поля: {str(e)}")
        await state.clear()
    return
