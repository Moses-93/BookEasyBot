import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.service import CreateServiceState, UpdateServiceState, DeleteServiceState
from keyboards.admin import inline_keyboard


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "📖 Послуги")
async def show_manage_services(message: Message):
    await message.answer(
        text="Ви перейли в розділ керування послугами!",
        reply_markup=admin_keyboard.manage_services(),
    )


@router.message(F.text == "➕ Додати послугу")
async def start_create_service(message: Message, state: FSMContext):
    await message.answer(text="Введіть назву послуги")
    await state.set_state(CreateServiceState.name)
    return


@router.message(F.text == "Видалити послугу")
async def start_delete_service(message: Message, state: FSMContext):
    services = await api_client.get(endpoint="/services/", chat_id=message.from_user.id)
    keyboard = inline_keyboard.main(data=services, name="name", callback="id")
    await message.answer(
        text="Оберіть послугу, яку ви бажаєте видалити:", reply_markup=keyboard
    )
    await state.set_state(DeleteServiceState.service)
    return


@router.message(F.text == "Редагувати послугу")
async def start_edit_service(message: Message, state: FSMContext):
    services = await api_client.get(endpoint="/services/", chat_id=message.from_user.id)
    keyboard = inline_keyboard.main(data=services, name="name", callback="id")
    await message.answer(
        text="Оберіть послугу, яку ви бажаєте редагувати:", reply_markup=keyboard
    )
    await state.set_state(UpdateServiceState.name)
    return


@router.callback_query(CreateServiceState.name)
async def set_service_name(callback: CallbackQuery, state: FSMContext):
    await state.update_data(name=callback.data)
    await callback.message.answer(text="Введіть ціну послуги")
    await state.set_state(CreateServiceState.price)
    return


@router.callback_query(CreateServiceState.price)
async def set_service_price(callback: CallbackQuery, state: FSMContext):
    await state.update_data(price=callback.data)
    service_data = await state.get_data()
    response = await api_client.post(
        endpoint="/services/", chat_id=callback.from_user.id, data=service_data
    )
    if response.status == 201:
        await callback.message.answer(text="Послуга успішно додана!")
        await state.clear()
    else:
        await callback.message.answer(text="Помилка при додаванні послуги!")
    await state.clear()
    return


@router.callback_query(DeleteServiceState.service)
async def delete_service(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data
    if not service_id:
        await callback.message.reply(
            text="На жаль сталася помилка. Спробуйте будь ласка пізніше"
        )
        return
    response = await api_client.delete(
        endpoint=f"/services/{service_id}/", chat_id=callback.from_user.id
    )
    if response.status_code == 204:
        await callback.message.answer(text="Послуга успішно видалена!")
        await state.clear()
        return
    await callback.message.answer(text="Помилка при видаленні послуги!")
    await state.clear()
    return


@router.callback_query(UpdateServiceState.name)
async def choice_service_field(callback: CallbackQuery, state: FSMContext):
    await state.update_data(service_id=callback.data)
    keyboard = inline_keyboard.choose_field(fields={"Назва": "name", "Ціна": "price"})
    await callback.message.answer(
        text="Оберіть поле, яке ви бажаєте змінити:", reply_markup=keyboard
    )
    await state.set_state(UpdateServiceState.field)
    return


@router.callback_query(UpdateServiceState.field)
async def update_service_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data
    await state.update_data(field=field)
    await callback.message.answer(text=f"Введіть нове значення поля {field.capitalize()}")
    await state.set_state(UpdateServiceState.new_value)
    return


@router.callback_query(UpdateServiceState.new_value)
async def set_new_service_value(callback: CallbackQuery, state: FSMContext):
    service = await state.get_data()
    service_id = service.get("service_id")
    field = service.get("field")
    new_value = callback.data
    if not service_id or not field or not new_value:
        await callback.message.reply(
            text="На жаль сталася помилка. Спробуйте будь ласка пізніше"
        )
        return
    response = await api_client.patch(
        endpoint=f"/services/{service_id}/",
        chat_id=callback.from_user.id,
        json={field: new_value},
    )

    if response.status == 200:
        await callback.message.answer(text=f"Значення поля {field} успішно змінено!")
        await state.clear()
        return
    await callback.message.answer(text="Помилка при зміні значення поля!")
    await state.clear()
    return
