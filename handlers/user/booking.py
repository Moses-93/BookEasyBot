import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.booking import BookingStates, CancelBook
from keyboards.general import display_data_keyboard
from keyboards import general, user
from services.api_client import api_client
from utils.utils import calculate_reminder_time

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
    await state.set_state(BookingStates.service)


@router.callback_query(BookingStates.master)
async def select_master(callback: CallbackQuery, state: FSMContext):
    master_id = callback.data
    await state.update_data(master_id=master_id)
    status, services = await api_client.get(
        f"/services?master_id={master_id}", callback.from_user.id
    )
    await handle_api_response(
        status,
        display_data_keyboard.service_keyboard(services),
        callback.message,
        MESSAGES["select_master_success"],
    )
    await state.set_state(BookingStates.service)
    await callback.answer()


@router.callback_query(BookingStates.service)
async def select_service(callback: CallbackQuery, state: FSMContext):
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
        display_data_keyboard.date_keyboard(dates),
        callback.message,
        MESSAGES["select_service_success"],
    )
    await state.set_state(BookingStates.date)
    await callback.answer()


@router.callback_query(BookingStates.date)
async def select_date(callback: CallbackQuery, state: FSMContext):
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
        display_data_keyboard.time_keyboard(times),
        callback.message,
        MESSAGES["select_date_success"],
    )
    await state.set_state(BookingStates.time)
    await callback.answer()


@router.callback_query(BookingStates.time)
async def select_time(callback: CallbackQuery, state: FSMContext):
    time_id, time = callback.data.split(f":", 1)
    await state.set_state(BookingStates.reminder_offset)
    await state.update_data(time_id=time_id, time=time)
    await send_message(
        callback.message,
        MESSAGES["select_reminder_offset"],
        reply_markup=general.dynamic_keyboard.dynamic_inline_keyboard(
            {"Не отримувати нагадування": "skip_reminder"}
        ),
    )
    await callback.answer()


@router.message(BookingStates.reminder_offset)
async def select_reminder_offset(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        offset = int(message.text)
    except ValueError:
        await send_message(message, "Вкажіть ціле число. Спробуйте знову")
        return
    reminder_time = calculate_reminder_time(data, offset)
    await state.update_data(reminder_time=str(reminder_time))
    await confirm_booking(message, state)


@router.callback_query(F.data == "skip_reminder")
async def skip_reminder(callback: CallbackQuery, state: FSMContext):
    await confirm_booking(callback.message, state)


@router.callback_query(F.data == "confirm_booking")
async def create_booking(callback: CallbackQuery, state: FSMContext, user_id):
    data = await state.get_data()
    if not data:
        await send_message(callback.message, MESSAGES["incomplete_booking_form"])
        return
    status, new_booking = await api_client.post("/bookings", user_id, json=data)
    if status == 201:
        await send_message(
            callback,
            MESSAGES["booking_success"].format(
                service=new_booking["service"]["name"],
                date=new_booking["date"]["date"],
                time=new_booking["time"]["time"],
            ),
        )
    await state.clear()


@router.callback_query(F.data == "cancel_process_booking")
async def cancel_process_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await send_message(
        callback.message,
        MESSAGES["cancel_process_booking"],
        reply_markup=user.user_keyboard.main_keyboard(),
    )


@router.callback_query(CancelBook.book)
async def cancel_book(callback: CallbackQuery, state: FSMContext):
    book_id = callback.data
    status, msg = await api_client.patch(
        f"/bookings/{book_id}", chat_id=callback.from_user.id
    )
    if status == 204:
        await send_message(callback, MESSAGES["cancel_booking_success"])
