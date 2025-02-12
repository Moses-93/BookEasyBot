import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from typing import List, Dict
from urllib.parse import urlencode

from services.api_client import api_client
from utils.formatted_view import format_booking
from keyboards.general import (
    Paginator,
    manage_booking_keyboard as booking_keyboard,
    dynamic_keyboard,
)
from keyboards.user import user_keyboard

logger = logging.getLogger(__name__)

router = Router()

MESSAGES = {
    "category": "📅 Оберіть категорію, яку ви хочете переглянути!",
    "chose_booking": "🔍 Оберіть, який запис ви хочете скасувати!",
    "successful_cancel": "✅ Ви успішно скасували ваш запис до майстра!",
    "back_to_main_menu": "🔙 Ви повернулись до головного меню",
}

ENDPOINT = "/bookings"


async def show_bookings(message: Message, bookings: List[Dict], callback_prefix: str):
    offset, limit = 0, 5
    has_more = len(bookings) > limit
    bookings = bookings[:limit]

    paginator = Paginator(offset, limit)
    await message.answer(
        text=str(format_booking(bookings)),
        reply_markup=paginator.pagination_keyboard(has_more, callback_prefix),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["📖 Мої записи", "📒 Записи"]))
async def my_bookings(message: Message):
    logger.info("Starting booking handler")
    keyboard = booking_keyboard.manage_bookings(is_master=message.text == "📒 Записи")
    await message.answer(
        text=MESSAGES["category"],
        reply_markup=keyboard,
    )


@router.message(F.text == "📂 Активні записи")
async def show_active_bookings(message: Message):
    _, bookings = await api_client.get(
        "/bookings?active=True&limit=6", chat_id=message.from_user.id
    )
    await show_bookings(message, bookings, "active_bookings")


@router.message(F.text == "🗄️ Архів записів")
async def show_all_bookings(message: Message):
    _, bookings = await api_client.get(
        "/bookings?limit=6", chat_id=message.from_user.id
    )
    await show_bookings(message, bookings, "all_bookings")


@router.message(F.text == "❌ Скасувати запис")
async def cancel_booking(message: Message, user_id):
    params = {"active": True, "limit": 6}
    query_string = urlencode(params)
    url = f"{ENDPOINT}?{query_string}"
    _, bookings = await api_client.get(url, user_id)
    await message.answer(text=MESSAGES["chose_booking"])
    for booking in bookings:
        await message.answer(
            text=str(format_booking(booking, single=True)),
            reply_markup=dynamic_keyboard.dynamic_inline_keyboard(
                {"❌ Скасувати": f"cancel_{booking['id']}"}
            ),
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith(("active_bookings", "all_bookings")))
async def paginate_bookings(callback: CallbackQuery):
    prefix, action, new_offset, limit = callback.data.split(":")
    new_offset, limit = int(new_offset), int(limit)
    logger.info(f"Offset:{new_offset}, prefix:{prefix}, limit:{limit}, action:{action}")

    params = {"offset": new_offset, "limit": limit + 1}

    if prefix == "active_bookings":
        params["active"] = True

    query_string = urlencode(params)
    url = f"{ENDPOINT}?{query_string}"

    status, bookings = await api_client.get(url, chat_id=callback.from_user.id)

    if status == 200:
        has_more = len(bookings) > limit
        bookings = bookings[:limit]

        paginator = Paginator(new_offset, limit)
        await callback.message.edit_text(
            text=str(format_booking(bookings)),
            reply_markup=paginator.pagination_keyboard(has_more, prefix),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("cancel_"))
async def cancel_booking(callback: CallbackQuery, user_id):
    booking_id = callback.data.split("_")[1]
    await api_client.patch(endpoint=f"{ENDPOINT}/{booking_id}/", chat_id=user_id)
    await callback.message.answer(text=MESSAGES["successful_cancel"])
    await callback.answer()


@router.message(F.text == "⬅️ Назад")
async def back_to_main_menu(message: Message):
    await message.answer(
        text=MESSAGES["back_to_main_menu"],
        reply_markup=user_keyboard.main_keyboard(),
    )
