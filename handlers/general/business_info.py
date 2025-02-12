import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from core.constants import WARNING_MESSAGE
from services.api_client import api_client
from states import business_info
from utils.formatted_view import (
    format_business_info,
    format_reviews,
)
from keyboards.general import display_data_keyboard as keyboard, dynamic_keyboard

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "Відгуки")
async def feedback(message: Message, user_id: int):
    response = await api_client.get(endpoint="/feedbacks/", chat_id=user_id)
    await message.answer(
        text=str(format_reviews(response)),
        reply_markup=dynamic_keyboard.create_reply_keyboard(
            button_names=["Залишити відгук"]
        ),
        parse_mode="Markdown",
    )


@router.message(F.text == "📕 Контакти")
async def contact_info(message: Message, state: FSMContext, user_id: int):
    status, data = await api_client.get(endpoint="/business-info/", chat_id=user_id)
    if status == 409:
        logger.warning("В користувача виявлено кілька майстрів")
        await message.answer(
            text=WARNING_MESSAGE["multiple_masters"],
            reply_markup=keyboard.choice_master(data),
        )
        await state.set_state(business_info.ChoiceMasterState.master)
        return

    await message.answer(text=str(format_business_info(data)), parse_mode="Markdown")


@router.callback_query(business_info.ChoiceMasterState.master)
async def choice_master_for_business_info(callback: CallbackQuery, user_id: int):
    logger.info("Starting choice master for business info")
    master_id = callback.data
    _, services = await api_client.get(
        endpoint=f"/business-info?master_id={master_id}", chat_id=user_id
    )

    await callback.message.answer(
        text=str(format_business_info(services)), parse_mode="Markdown"
    )
    await callback.answer()
