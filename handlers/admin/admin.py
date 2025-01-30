import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.admin import SetAdminState, DeleteAdminState
from keyboards.admin import reply_keyboard, inline_keyboard
from utils.formatted_view import format_admin


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "Адміністратори")
async def start(message: Message):
    await message.answer(
        text="Ви перейшли в керування адміністраторами!\nОберіть потрібну вам дію",
        reply_markup=reply_keyboard.admin(),
    )
    return


@router.message(F.text == "Призначити адміністратора")
async def assign_admin(message: Message, state: FSMContext):
    await state.set_state(SetAdminState.name)
    await message.answer(text="Введіть ім'я адміністратора")


@router.message(F.text == "Видалити адміністратора")
async def delete_admin(message: Message, state: FSMContext):
    await state.set_state(DeleteAdminState.admin_id)
    admins = await api_client.get(endpoint="/users/", chat_id=message.from_user.id)
    keyboard = inline_keyboard.main(data=admins, name="name", callback="id")
    await message.answer(
        text="Оберіть адміністратора, якого ви бажаєте видалити:", reply_markup=keyboard
    )


@router.message(F.text == "Список адміністраторів")
async def list_admins(message: Message):
    admins = await api_client.get(endpoint="/users/", chat_id=message.from_user.id)
    if not admins:
        await message.answer(text="Список адміністраторів порожній!")
        return
    await message.answer(text=format_admin(admins), parse_mode="Markdown")


@router.message(SetAdminState.name)
async def set_admin_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text="Введіть чат ID адміністратора!")
    await state.set_state(SetAdminState.chat_id)


@router.message(SetAdminState.chat_id)
async def set_admin_chat_id(message: Message, state: FSMContext):
    try:
        chat_id = int(message.text)
    except ValueError:
        await message.answer(text="Невірно введений чат ID!")
        return
    await state.update_data(chat_id=chat_id, role="admin")
    data = await state.get_data()
    logger.info(f"Data: {data}")
    response = await api_client.post(
        endpoint="/users/", chat_id=message.from_user.id, json=data
    )
    if response.status == 201:
        await message.answer(text="Адміністратор успішно доданий!")
        await state.clear()
        return
    await message.answer(text="Помилка при додаванні адміністратора!")
    await state.clear()
    return


@router.callback_query(DeleteAdminState.admin_id)
async def delete_admin_id(callback: CallbackQuery, state: FSMContext):
    admin_id = callback.data
    await state.update_data(admin_id=admin_id)
    response = await api_client.delete(
        endpoint=f"/users/{admin_id}", chat_id=callback.from_user.id
    )
    if response:
        await callback.message.answer(text="Адміністратор успішно видалений!")
        await state.clear()
        return
    await callback.message.answer(text="Помилка при видаленні адміністратора!")
    await state.clear()
    return
