import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.booking import BookingStates
from keyboards.booking import booking_keyboard
from keyboards.general import dynamic_keyboard, general_reply_keyboard
from services.api_client import api_client
from utils.formatted_view import format_booking

router = Router()
logger = logging.getLogger(__name__)

MESSAGES = {
    "start_booking": "👋 Вітаємо в системі бронювання! Тут ви можете записатися на послугу. Давайте почнемо! Оберіть послугу зі списку нижче:",
    "multiple_masters": "🤔 Ой, схоже у вас не один майстер! Будь ласка, оберіть, до кого ви хочете записатися:",
    "error_services": "😔 На жаль, сталася помилка при отриманні послуг. Спробуйте ще раз або зверніться до підтримки.",
    "my_bookings": "📅 Ось ваші записи! Оберіть категорію, яку ви хочете переглянути:",
    "back_to_main": "🏠 Ви повернулися до головного меню. Що бажаєте зробити далі?",
    "select_master_success": "🎉 Чудовий вибір! Тепер оберіть послугу, яку ви хочете замовити:",
    "select_master_error": "😅 Упс! Щось пішло не так. Спробуйте будь ласка пізніше!",
    "no_services": "😕 Наразі доступних послуг немає. Спробуйте іншого майстра або зайдіть пізніше!",
    "select_service_success": "📅 Чудово! Тепер оберіть бажану дату для запису:",
    "select_service_error": "😔 На жаль, сталася помилка при отриманні доступних дат. Спробуйте ще раз!",
    "no_dates": "😕 Наразі доступних дат немає. Спробуйте іншого майстра або зайдіть пізніше!",
    "select_date_success": "⏰ Супер! Тепер оберіть зручний для вас час:",
    "select_date_error": "😔 На жаль, сталася помилка при отриманні доступного часу. Спробуйте ще раз!",
    "no_times": "😕 Наразі доступного часу немає. Спробуйте іншу дату або зайдіть пізніше!",
    "booking_success": "🎉 Вітаємо! Ви успішно записалися. Ми чекаємо на вас!",
    "booking_error": "😔 На жаль, сталася помилка при створенні запису. Спробуйте ще раз або зверніться до підтримки.",
    "no_booking": "😕 На жаль, у вас поки немає записів, але, ви можете це швидко виправити",
    "api_error": "😕 Упс! Щось пішло не так. Помилка: {error}. Спробуйте ще раз або зверніться до підтримки.",
    "all_bookings": "📋 Ось всі ваші записи:",
    "active_bookings": "📌 Ось ваші активні записи:",
}


async def handle_api_response(
    status: int, data, message: Message, success_message: str, error_message: str
):
    if status == 200:
        await message.answer(success_message, reply_markup=data)
    elif status == 404:
        await message.answer(
            MESSAGES["no_services"]
            if "services" in success_message
            else MESSAGES["no_dates"]
        )
    else:
        await message.answer(error_message)


@router.message(F.text == "Записатись")
async def start_booking(message: Message, state: FSMContext):
    """
    Початок процесу бронювання: вибір послуги.
    """
    try:
        status, datas = await api_client.get("/services/", message.from_user.id)
        if status == 200:
            await message.answer(
                MESSAGES["start_booking"],
                reply_markup=booking_keyboard.service_keyboard(datas),
            )
            await state.set_state(BookingStates.service)
        elif status == 409:
            await message.answer(
                MESSAGES["multiple_masters"],
                reply_markup=booking_keyboard.choice_master(datas),
            )
            await state.set_state(BookingStates.master)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply(MESSAGES["error_services"])


@router.message(F.text == "Мої записи")
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


@router.message(F.text == "Назад")
async def back_to_main_menu(message: Message):
    await message.answer(
        text=MESSAGES["back_to_main"],
        reply_markup=general_reply_keyboard.main_keyboard(),
    )


@router.callback_query(BookingStates.master)
async def select_master(callback: CallbackQuery, state: FSMContext):
    master_id = callback.data
    await state.update_data(master_id=master_id)
    status, services = await api_client.get(
        f"/services?master_id={master_id}", callback.from_user.id
    )
    await handle_api_response(
        status,
        booking_keyboard.service_keyboard(services),
        callback.message,
        MESSAGES["select_master_success"],
        MESSAGES["select_master_error"],
    )
    await state.set_state(BookingStates.service)
    await callback.answer()


@router.callback_query(BookingStates.service)
async def select_service(callback: CallbackQuery, state: FSMContext):
    """
    Обробка вибору послуги.
    """
    data = await state.get_data()
    master_id = data.get("master_id")
    await state.update_data(service_id=callback.data)
    status, dates = await api_client.get(
        f"/dates?master_id={master_id}" if master_id else "/dates/",
        callback.from_user.id,
    )
    await handle_api_response(
        status,
        booking_keyboard.date_keyboard(dates),
        callback.message,
        MESSAGES["select_service_success"],
        MESSAGES["select_service_error"],
    )
    await state.set_state(BookingStates.date)
    await callback.answer()


@router.callback_query(BookingStates.date)
async def select_date(callback: CallbackQuery, state: FSMContext):
    """
    Обробка вибору дати.
    """
    date_id = callback.data
    data = await state.get_data()
    master_id = data.get("master_id")
    await state.update_data(date_id=date_id)
    status, times = await api_client.get(
        (
            f"/times/?date_id={date_id}&master_id={master_id}"
            if master_id
            else f"/times/?date_id={date_id}"
        ),
        callback.from_user.id,
    )
    await handle_api_response(
        status,
        booking_keyboard.time_keyboard(times),
        callback.message,
        MESSAGES["select_date_success"],
        MESSAGES["select_date_error"],
    )
    await state.set_state(BookingStates.time)
    await callback.answer()


@router.callback_query(BookingStates.time)
async def select_time(callback: CallbackQuery, state: FSMContext):
    """
    Обробка введення часу та завершення збору даних.
    """
    await state.update_data(time_id=callback.data)
    data = await state.get_data()
    master_id = data.get("master_id")
    try:
        status, response_data = await api_client.post(
            f"/bookings?master_id={master_id}" if master_id else "/bookings/",
            callback.from_user.id,
            json=data,
        )
        if status == 201:
            await callback.message.answer(MESSAGES["booking_success"])
            await callback.answer()
        elif status == 400:
            await callback.message.answer(MESSAGES["booking_error"])
    except Exception as e:
        await callback.message.reply(
            f"Сталася помилка при створенні бронювання: {str(e)}"
        )
    finally:
        await state.clear()


@router.callback_query(F.data == "all_bookings")
async def show_all_bookings(callback: CallbackQuery):
    status, bookings = await api_client.get(
        endpoint="/bookings/", chat_id=callback.from_user.id
    )
    if status == 200:
        await callback.message.answer(
            MESSAGES["all_bookings"], reply_markup=str(format_booking(bookings))
        )
        await callback.answer()
        return
    elif status == 404:
        await callback.message.answer(MESSAGES["no_booking"])
        await callback.answer()
        return
    else:
        await callback.message.answer(MESSAGES["api_error"].format(error=bookings))
        await callback.answer()
        return


@router.callback_query(F.data == "active_bookings")
async def show_active_bookings(callback: CallbackQuery):
    status, bookings = await api_client.get(
        endpoint="/bookings?active=True", chat_id=callback.from_user.id
    )
    if status == 200:
        await callback.message.answer(
            MESSAGES["all_bookings"], reply_markup=str(format_booking(bookings))
        )
        await callback.answer()
        return
    elif status == 404:
        await callback.message.answer(MESSAGES["no_booking"])
        await callback.answer()
        return
    else:
        await callback.message.answer(MESSAGES["api_error"].format(error=bookings))
        await callback.answer()
        return
