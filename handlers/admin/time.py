import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.time import CreateTimeStates, DeleteTimeStates
from keyboards.general import display_data_keyboard


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "➕⏰ Додати час")
async def start_add_time(message: Message, state: FSMContext):
    status, dates = await api_client.get(
        endpoint="/dates", chat_id=message.from_user.id
    )
    if status == 200:
        await message.answer(
            text="Оберіть дату, до якої ви бажаєте додати час!",
            reply_markup=display_data_keyboard.date_keyboard(dates),
        )
        await state.set_state(CreateTimeStates.date)
        return
    elif status == 404:
        await message.answer(
            text="Ви не можете додати час до неіснуючої дати:)\nСпочатку додайте дату, а потім продовжимо"
        )
        return

    else:
        await message.answer(
            text="Виникла невідома помилка!\n Спробуйте звернутись до адміністратора бота"
        )
        return


@router.message(F.text == "Видалити час")
async def start_delete_time(message: Message, state: FSMContext):
    dates = await api_client.get(endpoint="/dates", chat_id=message.from_user.id)
    await message.answer(
        text="Оберіть дату, в якій бажаєте видалити доступний час!",
        reply_markup=display_data_keyboard.date_keyboard(dates),
    )
    await state.set_state(DeleteTimeStates.date)
    return


@router.callback_query(CreateTimeStates.date)
async def select_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateTimeStates.time)
    date_id, date = callback.data.split(":")
    await state.update_data(date_id=date_id, date=date)
    await callback.message.answer("Введіть час (у форматі HH:MM):")
    await callback.answer()
    return


@router.message(CreateTimeStates.time)
async def add_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    data = await state.get_data()
    logger.info(f"Data: {data}")
    try:
        status, msg = await api_client.post("/times/", message.from_user.id, json=data)
        if status == 201:
            await message.reply(f"Час успішно доданий!")
            await state.clear()
        elif status == 400 or 422:
            await message.answer(text=f"Виникла помилка:{str(msg)}")
            await state.clear()

    except Exception as e:
        await message.reply(f"Сталася помилка при додаванні часу: {str(e)}")

    await state.clear()


@router.callback_query(DeleteTimeStates.date)
async def select_date_delete(callback: CallbackQuery, state: FSMContext):
    date_id = callback.data
    await state.update_data(date_id=date_id)
    times = await api_client.get(
        endpoint=f"/times/{date_id}", chat_id=callback.from_user.id
    )
    keyboard = inline_keyboard.main(data=times, name="time", callback="id")
    await callback.message.answer(
        "Оберіть, який час ви бажаєте видалити:", reply_markup=keyboard
    )
    await state.set_state(DeleteTimeStates.time)


@router.callback_query(DeleteTimeStates.time)
async def delete_time(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time_id=callback.data)
    time = await state.get_data()
    response = await api_client.delete(
        endpoint=f"/times/{time["time_id"]}/{time["date_id"]}",
        chat_id=callback.from_user.id,
    )
    if response.status_code == 204:
        await callback.message.answer("Час успішно видалено!")
        await state.clear()
        return
    await callback.message.answer("Помилка при видаленні часу!")
    await state.clear()
    return
