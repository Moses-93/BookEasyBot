import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.api_client import api_client
from states import time, date, service, business_info
from utils.formatted_view import (
    format_business_info,
    format_service,
    format_date,
    format_time,
)
from keyboards.booking import booking_keyboard


logger = logging.getLogger(__name__)

router = Router()

MESSAGES = {
    "my_bookings": "📅 Ось ваші записи! Оберіть категорію, яку ви хочете переглянути:",
    "all_bookings": "📋 Ось всі ваші записи:",
}


@router.message(F.text == "Історія записів")
async def my_bookings(message: Message):
    await message.answer(
        text=MESSAGES["my_bookings"],
        reply_markup=dynamic_keyboard.dynamic_inline_keyboard(
            button_names={
                "Всі записи": "all_bookings",
                "Активні записи": "active_bookings",
            }
        ),
    )


@router.message(F.text == "Контакти")
async def contact_info(message: Message, state: FSMContext):
    status, data = await api_client.get(
        endpoint="/business-info/", chat_id=message.from_user.id
    )
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text="У вас виявлено декілька майстрів!\nОберіть потрібного!",
            reply_markup=booking_keyboard.choice_master(data),
        )
        await state.set_state(business_info.ChoiceMasterState.master)
        return

    elif status == 404:
        await message.answer(
            text="Контактна інформація відсутня!\nЗверніться будь ласка до свого майстра"
        )
        return

    elif status == 200:
        await message.answer(text=format_business_info(data), parse_mode="Markdown")
        return


@router.message(F.text == "Доступні послуги")
async def start_booking(message: Message, state: FSMContext):
    user_id = message.from_user.id
    status, data = await api_client.get(endpoint="/services/", chat_id=user_id)
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text="У вас виявлено декілька майстрів!\nОберіть потрібного!",
            reply_markup=booking_keyboard.choice_master(data),
        )
        await state.set_state(service.ChoiceMasterState.master)
        return

    elif status == 404:
        await message.answer(text="Доступних послуг поки немає")
        return

    elif status == 200:
        services = format_service(data=data)
        await message.answer(text=services, parse_mode="Markdown")
        return
    else:
        message.answer(text="Сталася невідома помилка! Спробуйте будь ласка пізніше")
        return


@router.message(F.text == "Доступні дати")
async def show_date(message: Message, state: FSMContext):
    status, data = await api_client.get(
        endpoint="/dates/", chat_id=message.from_user.id
    )

    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text="У вас виявлено декілька майстрів!\nОберіть потрібного!",
            reply_markup=booking_keyboard.choice_master(data),
        )
        await state.set_state(date.ChoiceMasterDate.master)
        return

    elif status == 404:
        await message.answer(text="Доступних дат поки немає")
        return

    elif status == 200:
        await message.answer(text=str(format_date(data)), parse_mode="Markdown")
        return
    else:
        message.answer(text="Сталася невідома помилка! Спробуйте будь ласка пізніше")
        return


@router.message(F.text == "Доступний час")
async def start_show_time(message: Message, state: FSMContext):
    status, data = await api_client.get(endpoint="/dates", chat_id=message.from_user.id)
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text="У вас виявлено декілька майстрів!\nОберіть потрібного!",
            reply_markup=booking_keyboard.choice_master(data),
        )
        await state.set_state(time.ChoiceMasterTime.master)
        return
    await message.answer(
        text="Оберіть дату, в якій бажаєте переглянути доступний час!",
        reply_markup=booking_keyboard.date_keyboard(data),
    )
    await state.set_state(time.ShowTimeStates.date)
    return


@router.callback_query(time.ChoiceMasterTime.master)
async def choice_master_for_time(callback: CallbackQuery, state: FSMContext):
    logger.info("Starting choice master for time")
    master_id = callback.data

    status, dates = await api_client.get(
        f"/dates?master_id={master_id}", callback.from_user.id
    )
    if status == 200:
        await state.set_state(time.ShowTimeStates.date)
        await state.update_data(master_id=master_id)
        await callback.message.answer(
            text="Оберіть дату, в якій бажаєте переглянути доступний час!",
            reply_markup=booking_keyboard.date_keyboard(dates),
        )
        await callback.answer()
        return
    elif status == 404:
        await callback.message.answer(text="Доступного часу поки немає!")
        await callback.answer()
        return
    else:
        await callback.message.answer(
            "Сталася невідома помилка! Спробуйте будь ласка пізніше!"
        )
        await callback.answer()
        return


@router.callback_query(time.ShowTimeStates.date)
async def select_date(callback: CallbackQuery, state: FSMContext):
    date_id = callback.data
    data = await state.get_data()
    logger.info(f"Data:{data}")
    status, times = await api_client.get(
        endpoint=f"/times?date_id={date_id}&master_id={data.get("master_id")}",
        chat_id=callback.from_user.id,
    )
    if status == 200:
        await callback.message.answer(
            text=str(format_time(times)), parse_mode="Markdown"
        )
        await callback.answer()
        await state.clear()
        return

    elif status == 404:
        await callback.message.answer(text="На жаль, доступного часу поки немає!")
        await callback.answer()
        await state.clear()
        return

    else:
        await callback.message.answer(
            "Сталася невідома помилка! Спробуйте будь ласка пізніше!"
        )
        await callback.answer()
        return


@router.callback_query(service.ChoiceMasterState.master)
async def choice_master_for_service(callback: CallbackQuery):
    logger.info("Starting choice master for service")
    master_id = callback.data
    status, services = await api_client.get(
        f"/services?master_id={master_id}", callback.from_user.id
    )
    if status == 200:
        await callback.message.answer(
            text=str(format_service(services)), parse_mode="Markdown"
        )
        await callback.answer()
        return
    elif status == 404:
        await callback.message.answer(text="Доступних послуг поки немає!")
        await callback.answer()
        return
    else:
        await callback.message.answer(
            "Сталася невідома помилка! Спробуйте будь ласка пізніше!"
        )
        await callback.answer()
        return


@router.callback_query(business_info.ChoiceMasterState.master)
async def choice_master_for_business_info(callback: CallbackQuery):
    logger.info("Starting choice master for business info")
    master_id = callback.data
    status, services = await api_client.get(
        f"/business-info?master_id={master_id}", callback.from_user.id
    )
    if status == 200:
        await callback.message.answer(
            text=str(format_business_info(services)), parse_mode="Markdown"
        )
        await callback.answer()
        return
    elif status == 404:
        await callback.message.answer(
            text="Контактна інформація відсутня!\nЗверніться будь ласка до свого майстра"
        )
        await callback.answer()
        return
    else:
        callback.message.answer(
            "Сталася невідома помилка! Спробуйте будь ласка пізніше!"
        )


@router.callback_query(date.ChoiceMasterDate.master)
async def choice_master_for_date(callback: CallbackQuery):
    logger.info("Starting choice master for date")
    master_id = callback.data
    status, dates = await api_client.get(
        f"/dates?master_id={master_id}", callback.from_user.id
    )
    if status == 200:
        logger.info(f"Dates:{dates}")
        await callback.message.answer(
            text=str(format_date(dates)), parse_mode="Markdown"
        )
        await callback.answer()
        return
    elif status == 404:
        await callback.message.answer(text="Доступних дат поки немає!")
        await callback.answer()
        return
    else:
        await callback.message.answer(
            "Сталася невідома помилка! Спробуйте будь ласка пізніше!"
        )
        await callback.answer()
        return
