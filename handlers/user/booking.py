import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.booking import BookingStates
from keyboards.booking import booking_keyboard
from keyboards.general import dynamic_keyboard
from keyboards.general import general_reply_keyboard
from services.api_client import api_client


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "Записатись")
async def start_booking(message: Message, state: FSMContext):
    """
    Початок процесу бронювання: вибір послуги.
    """
    try:

        services = await api_client.get("/services", message.from_user.id)
        keyboard = booking_keyboard.service_keyboard(services)
        await message.answer("Оберіть послугу:", reply_markup=keyboard)
        await state.set_state(BookingStates.service)
    except Exception as e:
        logger.error(f"Error: {e}")
        return await message.reply(f"Помилка при отриманні послуг: {str(e)}")


@router.message(F.text == "Мої записи")
async def my_bookings(message: Message):
    await message.answer(
        text="Оберіть потрібну вам категрію",
        reply_markup=dynamic_keyboard.dynamic_inline_keyboard(button_names={"Всі записи":"all_bookings", "Активні записи":"active_bookings"}),
    )
    return


@router.message(F.text == "Назад")
async def back_to_main_menu(message: Message):
    await message.answer(
        text="Ви повернулися до головного меню",
        reply_markup=general_reply_keyboard.main_keyboard(),
    )
    return


@router.callback_query(BookingStates.service)
async def select_service(callback: CallbackQuery, state: FSMContext):
    """
    Обробка вибору послуги.
    """
    user_id = callback.from_user.id
    logger.info(f"Callback: {callback.data}")
    try:
        await state.update_data(service_id=callback.data)
        dates = await api_client.get(endpoint="/dates", chat_id=user_id)

        await callback.message.answer(
            "Оберіть дату:", reply_markup=booking_keyboard.date_keyboard(dates)
        )
        await state.set_state(BookingStates.date)
    except Exception as e:
        await callback.message.answer(f"Помилка при отриманні доступних дат: {str(e)}")


@router.callback_query(BookingStates.date)
async def select_date(callback: CallbackQuery, state: FSMContext):
    """
    Обробка вибору дати.
    """
    date_id = callback.data
    await state.update_data(date_id=date_id)
    times = await api_client.get(
        endpoint=f"/times/{date_id}", chat_id=callback.from_user.id
    )
    await callback.message.answer(
        text="Оберіть зручний для вас час:",
        reply_markup=booking_keyboard.time_keyboard(times),
    )
    await state.set_state(BookingStates.time)


@router.message(BookingStates.time)
async def select_time(message: Message, state: FSMContext):
    """
    Обробка введення часу та завершення збору даних.
    """
    await state.update_data(time=message.text)
    data = await state.get_data()
    logger.info(f"Data: {data}")
    try:
        response = await api_client.post("/bookings/", message.from_user.id, json=data)
        await message.reply(
            f"Ваше бронювання успішно створено! Деталі:\n"
            f"Послуга: {data['service']}\n"
            f"Дата: {data['date']}\n"
            f"Час: {message.text}"
        )
    except Exception as e:
        await message.reply(f"Сталася помилка при створенні бронювання: {str(e)}")

    await state.clear()


@router.callback_query(F.data == "all_bookings")
async def show_all_bookings(callback: CallbackQuery, user_id):
    response = await api_client.get(endpoint="/bookings/", chat_id=user_id)
    if response.status == 200:
        await callback.answer(text="Всі записи:")
        for booking in response.json():
            await callback.answer(
                text=f"Дата: {booking['date']}, ��ас: {booking['time']}, Статус: {booking['status']}"
            )
    await callback.answer(text="Записи на майбутній день")
    return


@router.callback_query(F.data == "active_bookings")
async def show_active_bookings(callback: CallbackQuery, user_id):
    response = await api_client.get(
        endpoint="/bookings/", chat_id=user_id, params={"active:": True}
    )
    if response.status == 200:
        await callback.answer(text="Активні записи:")
        for booking in response.json():
            await callback.answer(
                text=f"Дата: {booking['date']}, Час: {booking['time']}, Статус: {booking['status']}"
            )
    return