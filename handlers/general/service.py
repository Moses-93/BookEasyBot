import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.api_client import api_client
from states import service
from utils.formatted_view import format_service
from keyboards.general import display_data_keyboard as keyboard
from core.constants import WARNING_MESSAGE


logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text.in_(["📖 Послуги", "📋 Доступні послуги"]))
async def start_booking(message: Message, state: FSMContext, user_id: int):
    status, data = await api_client.get(endpoint="/services/", chat_id=user_id)
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text=WARNING_MESSAGE["multiple_masters"],
            reply_markup=keyboard.choice_master(data),
        )
        await state.set_state(service.ChoiceMasterState.master)
        return

    await message.answer(text=str(format_service(data)), parse_mode="Markdown")


@router.callback_query(service.ChoiceMasterState.master)
async def choice_master_for_service(callback: CallbackQuery, user_id: int):
    logger.info("Starting choice master for service")
    master_id = callback.data
    status, services = await api_client.get(f"/services?master_id={master_id}", user_id)

    await callback.message.answer(
        text=str(format_service(services)), parse_mode="Markdown"
    )
    await callback.answer()
