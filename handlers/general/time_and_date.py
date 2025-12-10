import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.api_client import api_client
from utils.formatted_view import format_time, format_date
from core.constants import WARNING_MESSAGE
from keyboards.general import display_data_keyboard as keyboard
from states import time, date


logger = logging.getLogger(__name__)

router = Router()

STATE = {
    "time": time.ChoiceMasterTime.master,
    "date": date.ChoiceMasterDate.master,
}


@router.message(F.text == "⏱️ Доступний час")
async def start_show_time(message: Message, state: FSMContext, user_id: int):
    status, data = await api_client.get(endpoint="/times", chat_id=user_id)
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text=WARNING_MESSAGE["multiple_masters"],
            reply_markup=keyboard.choice_master(data),
        )
        await state.set_state(STATE["time"])
        return
    await message.answer(text=str(format_time(data)), parse_mode="Markdown")


@router.message(F.text == "📅 Доступні дати")
async def show_date(message: Message, state: FSMContext, user_id: int):
    status, data = await api_client.get(endpoint="/dates/", chat_id=user_id)
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text=WARNING_MESSAGE["multiple_masters"],
            reply_markup=keyboard.choice_master(data),
        )
        await state.set_state(STATE["date"])
        return

    await message.answer(text=str(format_date(data)), parse_mode="Markdown")


@router.callback_query(STATE["time"])
async def choice_master_for_time(callback: CallbackQuery, user_id: int):
    logger.info("Starting choice master for time")
    master_id = callback.data

    _, times = await api_client.get(
        endpoint=f"/times?master_id={master_id}", chat_id=user_id
    )
    await callback.message.answer(text=str(format_time(times)))


@router.callback_query(STATE["date"])
async def choice_master_for_date(callback: CallbackQuery, user_id: int):
    logger.info("Starting choice master for date")
    master_id = callback.data
    _, dates = await api_client.get(
        endpoint=f"/dates?master_id={master_id}", chat_id=user_id
    )

    await callback.message.answer(text=str(format_date(dates)), parse_mode="Markdown")
    await callback.answer()
