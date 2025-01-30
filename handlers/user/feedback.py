import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.feedback import CreateFeedbackState
from keyboards.general import dynamic_keyboard
from utils.formatted_view import format_reviews


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "Відгуки")
async def feedback(message: Message):
    response = await api_client.get(
        endpoint="/feedbacks/", chat_id=message.from_user.id
    )
    keyboard = dynamic_keyboard.create_reply_keyboard(button_names=["Залишити відгук"])
    feedbacks = await format_reviews(response)
    await message.answer(text=feedbacks, reply_markup=keyboard, parse_mode="Markdown")


@router.message(F.text == "Залишити відгук")
async def start_create_feedback(message: Message, state: FSMContext):
    await state.set_state(CreateFeedbackState.rating)
    keyboard = dynamic_keyboard.create_reply_keyboard([str(i) for i in range(1, 6)])
    await message.answer(
        text="Оцініть роботу майстра від 1 - 5!", reply_markup=keyboard
    )


@router.message(CreateFeedbackState.rating)
async def create_feedback_rating(message: Message, state: FSMContext):
    await state.update_data(rating=int(message.text))
    keyboard = dynamic_keyboard.create_reply_keyboard(["Відправити відгук"])
    await message.answer(text="Додайте короткий опис!", reply_markup=keyboard)
    await state.set_state(CreateFeedbackState.comment)


@router.message(CreateFeedbackState.comment, F.text.casefold() == "відправити відгук")
async def send_feedback(message: CallbackQuery, state: FSMContext):
    logger.info("Запуск методу для відправки відгуку після натискання на кнопку")
    data = await state.get_data()
    logger.info(f"Data: {data}")
    response = await api_client.post(
        endpoint="/feedbacks/", chat_id=message.from_user.id, json=data
    )
    if response.status == 201:
        await message.answer(
            text="Відгук успішно відправлено!\nДякую, за виділений час!"
        )
        await state.clear()
        return
    await message.answer(text="Під час обробки виникла помилка!")
    await state.clear()
    return


@router.message(CreateFeedbackState.comment)
async def create_feedback_comment(message: Message, state: FSMContext):
    logger.info("Запуск методу для відправки відгуку")

    await state.update_data(comment=message.text)
    data = await state.get_data()
    response = await api_client.post(
        endpoint="/feedbacks/", chat_id=message.from_user.id, json=data
    )
    if response.status == 201:
        await message.answer(
            text="Відгук успішно відправлено!\nДякую, за виділений час!"
        )
        await state.clear()
        return
    await message.answer(text="Під час обробки виникла помилка!")
    await state.clear()
