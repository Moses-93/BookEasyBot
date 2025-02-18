from datetime import datetime, timedelta
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.booking import BookingStates, CancelBook
from keyboards.booking import booking_keyboard
from keyboards.general import dynamic_keyboard, general_reply_keyboard
from services.api_client import api_client
from utils.formatted_view import format_booking

router = Router()
logger = logging.getLogger(__name__)

MESSAGES = {
    "start_booking": "👋 Вітаємо в системі бронювання! Тут ви можете записатися на послугу. Почнімо!\nОберіть послугу зі списку нижче:",
    "multiple_masters": "🤔 Ой, схоже у вас не один майстер! Будь ласка, оберіть, до кого ви хочете записатися:",
    "back_to_main": "🏠 Ви повернулися до головного меню. Що бажаєте зробити далі?",
    "select_master_success": "🎉 Чудовий вибір! Тепер оберіть послугу, яку ви хочете замовити:",
    "select_service_success": "📅 Чудово! Тепер оберіть бажану дату для запису:",
    "select_date_success": "⏰ Супер! Тепер оберіть зручний для вас час:",
    "booking_success": "🎉 Вітаємо! Ви успішно записалися на послугу {service}. Ми чекаємо на вас {date} o {time}!",
    "active_bookings": "📌 Ось ваші активні записи:",
    "cancel_booking_success": "✅ Ваш запис успішно скасовано. Дякуємо, що скористалися нашими послугами!",
    "select_reminder_offset": "🌟 Відмінно!\nТепер вкажіть, за скільки годин до запису ви бажаєте отримати нагадування. ⏰",
    "confirm_booking": '🎉 Чудово! Ми майже закінчили.\n\nВи обрали послугу: **{service}**\nДата: **{date}**\nЧас: **{time}**\n\nЯкщо все вірно, натисніть кнопку "Підтвердити". Якщо бажаєте скасувати, натисніть "Скасувати". ❓',
    "cancel_process_booking": "😔 Нам шкода, що ви не записалися цього разу. Але ми завжди раді вас бачити! Чекаємо на вас знову! ❤️",
    "incomplete_booking_form": '😯 Ой, схоже, ви ще не заповнили форму для запису!\n\nБудь ласка, натисніть кнопку "📝 Новий запис", щоб продовжити.',
}


async def send_message(message: Message, text: str, reply_markup=None, parse_mode=None):
    await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)


async def handle_api_response(
    status: int, data, message: Message, success_message: str
):
    if status == 200:
        await send_message(message, success_message, reply_markup=data)


async def confirm_booking(message: Message, state: FSMContext):
    data = await state.get_data()
    keyboard = general.dynamic_keyboard.dynamic_inline_keyboard(
        {"✅ Підтвердити": "confirm_booking", "❌ Скасувати": "cancel_process_booking"}
    )
    msg = MESSAGES["confirm_booking"].format(
        service=data["service"], date=data["date"], time=data["time"]
    )
    await send_message(message, msg, reply_markup=keyboard, parse_mode="Markdown")


@router.message(F.text == "Назад")
async def back_to_main_menu(message: Message):
    await send_message(
        message,
        MESSAGES["back_to_main"],
        reply_markup=user.user_keyboard.main_keyboard(),
    )


@router.message(F.text == "📝 Новий запис")
async def start_booking(message: Message, state: FSMContext):
    status, data = await api_client.get("/services/", message.from_user.id)
    if status == 409:
        await send_message(
            message,
            MESSAGES["multiple_masters"],
            reply_markup=display_data_keyboard.choice_master(data),
        )
        await state.set_state(BookingStates.master)
    await send_message(
        message,
        MESSAGES["start_booking"],
        reply_markup=display_data_keyboard.service_keyboard(data),
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
    service_id, service = callback.data.split(":")
    master_id = data.get("master_id")
    logger.info(f"Service:{callback.data}")
    await state.update_data(service_id=service_id, service=service)
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
    date_id, date = callback.data.split(":")
    data = await state.get_data()
    master_id = data.get("master_id")
    await state.update_data(date_id=date_id, date=date)
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
    logger.info(f"Callback:{callback.data}")
    time_id, time = callback.data.split(f":", 1)
    await state.set_state(BookingStates.reminter_ofset)
    await state.update_data(time_id=time_id, time=time)
    await callback.message.answer(
        "Супер! А тепер вкажіть за скільки годин ви б хотіли отримати нагадування, але, не більше чим за 23 години",
        reply_markup=dynamic_keyboard.dynamic_inline_keyboard(
            {"Не отримувати нагадування": "skip"}
        ),
    )
    await callback.answer()


@router.message(BookingStates.reminter_ofset)
async def select_reminder_offset(message: Message, state: FSMContext):
    data = await state.get_data()
    master_id = data.get("master_id")
    if message.text != "skip":
        try:
            offset = int(message.text)
        except ValueError:
            await message.answer("Вкажіть ціле цисло. Спробуйте знову")
        date, time = data.get("date"), data.get("time")
        date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        reminder_time = date_time - timedelta(hours=offset)
        await state.update_data(reminder_time=str(reminder_time))
        data = await state.get_data()
        logger.info(f"Data:{data}")

    try:
        status, response_data = await api_client.post(
            f"/bookings?master_id={master_id}" if master_id else "/bookings/",
            message.from_user.id,
            json=data,
        )
        if status == 201:
            await message.answer(MESSAGES["booking_success"])
        elif status == 400:
            await message.answer(MESSAGES["booking_error"])
    except Exception as e:
        await message.reply(f"Сталася помилка при створенні бронювання: {str(e)}")
    finally:
        await state.clear()


@router.callback_query(F.data == "cancel_book")
async def start_cancel_book(callback: CallbackQuery, state: FSMContext):
    status, bookings = await api_client.get(
        "/bookings?active=True", chat_id=callback.from_user.id
    )
    if status == 200:
        await callback.message.answer(
            str(format_booking(bookings)), parse_mode="Markdown"
        )
        await callback.message.answer(
            "Оберіть, який запис ви хочете скасувати",
            reply_markup=booking_keyboard.cancel_booking(bookings),
        )
        await callback.answer()
        await state.set_state(CancelBook.book)
    else:
        await callback.message.answer("Помилка")


@router.callback_query(CancelBook.book)
async def cancel_book(callback: CallbackQuery, state: FSMContext):
    book_id = callback.data
    logger.info(f"Book_id: {book_id}")
    status, msg = await api_client.patch(
        f"/bookings/{book_id}", chat_id=callback.from_user.id
    )
    if status == 204:
        await callback.message.answer("Ви успішно скасували свій запис")
    else:
        await callback.message.answer("Помилка")
