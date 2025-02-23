from datetime import datetime
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.date import DeleteDateState, CreateDateState
from keyboards.admin import reply_keyboard, inline_keyboard


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "❌📅 Видалити дату")
async def delete_date(message: Message, state: FSMContext):
    user_id = message.from_user.id
    status, dates = await api_client.get(endpoint="/dates/", chat_id=user_id)
    if status == 200:
        await message.answer(
            text="Оберіть, яку дату ви бажаєте видалити",
            reply_markup=inline_keyboard.main_inline_keyboard(dates, "date", "id"),
        )
        await state.set_state(DeleteDateState.date)
        return
    if status == 404:
        await message.answer(text="У вас поки немає доступних дат!")
        return
    else:
        await message.answer(text="Виникла помилка! Спробуйте будь ласка пізніше!")
        return


@router.message(F.text == "Додати дату")
async def start_create_date(message: Message, state: FSMContext):
    await message.answer(text="Введіть нову дату в форматі YYYY-MM-DD")
    await state.set_state(CreateDateState.date)
    return


@router.message(CreateDateState.date)
async def add_date(message: Message, state: FSMContext):
    date = message.text
    await state.update_data(date=date)
    await state.set_state(CreateDateState.deactivation_time)
    await message.answer(
        text=f"Вкажіть в скільки годин дата повинна стати неактивною! Наприклад: якщо ви вкажете 17:00, {date} стане неактивною в {date} 17:00:00"
    )


@router.message(CreateDateState.deactivation_time)
async def create_date(message: Message, state: FSMContext):
    data = await state.get_data()
    date = data.get("date")
    deactivation_time = datetime.strptime(f"{date} {message.text}", "%Y-%m-%d %H:%M")
    status, msg = await api_client.post(
        endpoint="/dates/",
        chat_id=message.from_user.id,
        json={"date": date, "deactivation_time": str(deactivation_time)},
    )
    if status == 201:
        await message.answer(text="Дата успішно додана!")
        await state.clear()

    elif status >= 400:
        await message.answer(
            text=f"Виникла помилка при створенні нової дати:{str(msg)}"
        )
        await state.clear()


@router.callback_query(DeleteDateState.date)
async def delete_date(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    date_id = callback.data
    logger.info(f"Deleted date: {date_id}")
    status, msg = await api_client.delete(
        endpoint=f"/dates/{date_id}/", chat_id=user_id
    )
    if status == 204:
        await callback.message.answer(text="Вказана вами дата успішно видалена!")
        await state.clear()
        await callback.answer()
        return
    else:
        await callback.message.answer(text=f"При видаленні дати сталася помилка: {msg}")
        await state.clear()
        await callback.answer()
        return
