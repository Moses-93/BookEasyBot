from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Tuple

from keyboards.admin import AdminKeyboard
from keyboards.general import DisplayDataKeyboard
from states.service import CreateServiceState, DeleteServiceState, UpdateServiceState
from utils.validators import is_valid_price
from .service_query import ServiceQuery
from ..user import UserService


MESSAGE = {
    "start": "👋 Вітаю в розділі керування послугами! Тут ви можете створювати нові послуги, редагувати наявні або видаляти їх. Давайте разом зробимо ваш бізнес ще кращим!",
    "start_create_service": "🎯 Створімо нову послугу! Яка буде її назва? Напишіть її, будь ласка.",
    "start_deactivate_service": "🗑️ Щось зайве? Оберіть зі списку послугу, яку хочете видалити.",
    "start_edit_service": "✏️ Хочете щось покращити? Оберіть послугу, яку бажаєте оновити.",
    "input_service_name": "📝 Чудово! Дайте назву новій послузі.",
    "input_price": "💸 Супер! Тепер вкажіть вартість цієї послуги. Наприклад: 250 або 499.90 грн.",
    "input_new_value": "🔧 Майже готово! Введіть нове значення для поля {field}.",
    "select_field_to_update": "✨ Що саме ви хочете змінити? Оберіть поле, яке потрібно оновити.",
    "success_create_service": "🎉 Вітаю! Нова послуга успішно створена!\nНазва: {name}\nЦіна: {price} грн\nТепер клієнти можуть нею скористатися!",
    "success_delete_service": "✅ Готово! Послугу успішно видалено. Тепер список послуг став трохи акуратнішим!",
    "success_edit_field": "🎊 Вітаю! Поле {field} успішно оновлено. Нове значення: {new_field}.",
    "invalid_price": "🚨 Упс! Здається, вартість {price} вказана некоректно. Спробуйте ще раз, будь ласка!",
}


class ServiceCreateManager:

    def __init__(self, service_query: ServiceQuery):
        self.service_query = service_query

    async def start_create_service(self, state: FSMContext) -> str:
        await state.set_state(CreateServiceState.name)
        return MESSAGE["start_create_service"]

    async def set_service_name(self, state: FSMContext, name: str) -> str:
        await state.update_data(name=name)
        await state.set_state(CreateServiceState.price)
        return MESSAGE["input_price"]

    async def finish_create_service(
        self, state: FSMContext, price: str, user_id: int
    ) -> str:
        if not is_valid_price(price):
            return MESSAGE["invalid_price"].format(price=price)
        await state.update_data(price=price)
        service_data = await state.get_data()
        created_service = await self.service_query.create_service(user_id, service_data)
        await state.clear()
        return MESSAGE["success_create_service"].format(
            name=created_service["name"], price=created_service["price"]
        )


class ServiceDeactivateManager:

    def __init__(
        self, service_query: ServiceQuery, display_data_keyboard: DisplayDataKeyboard
    ):
        self.service_query = service_query
        self.display_data_keyboard = display_data_keyboard

    async def start_deactivate_service(
        self, state: FSMContext, user_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        services = await self.service_query.get_services(user_id)
        await state.set_state(DeleteServiceState.service)
        return MESSAGE[
            "start_deactivate_service"
        ], self.display_data_keyboard.service_keyboard(services)

    async def finish_deactivate_service(
        self, state: FSMContext, service_id: int, user_id: int
    ) -> str:
        await self.service_query.deactivate_service(user_id, service_id)
        await state.clear()
        return MESSAGE["success_delete_service"]


class ServiceEditManager:
    def __init__(
        self, service_query: ServiceQuery, display_data_keyboard: DisplayDataKeyboard
    ):
        self.service_query = service_query
        self.display_data_keyboard = display_data_keyboard

    async def start_edit_service(
        self, state: FSMContext, user_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        services = await self.service_query.get_services(user_id)
        await state.set_state(UpdateServiceState.name)
        return MESSAGE[
            "start_edit_service"
        ], self.display_data_keyboard.service_keyboard(services)

    async def create_field_selection(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        buttons = {"Назва": "name", "Вартість": "price"}
        for button, callback in buttons.items():
            keyboard.button(text=button, callback_data=callback)
        return keyboard.as_markup()

    async def select_field_to_update(
        self, state: FSMContext, service_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        await state.update_data(service_id=service_id)
        keyboard = await self.create_field_selection()
        await state.set_state(UpdateServiceState.field)
        return MESSAGE["select_field_to_update"], keyboard

    async def set_field(self, state: FSMContext, field: str) -> str:
        await state.update_data(field=field)
        await state.set_state(UpdateServiceState.new_value)
        return MESSAGE["input_new_value"].format(field=field)

    async def finish_update_service(
        self, state: FSMContext, new_value: str, user_id: int
    ) -> str:
        service_id = await state.get_value("service_id")
        field = await state.get_value("field")
        await self.service_query.update_service(user_id, service_id, {field: new_value})
        await state.clear()
        return MESSAGE["success_edit_field"]


class ServiceManager:
    def __init__(
        self,
        user_service: UserService,
        admin_keyboard: AdminKeyboard,
        service_create_manager: ServiceCreateManager,
        service_deactivate_manager: ServiceDeactivateManager,
        service_edit_manager: ServiceEditManager,
    ):
        self.user_service = user_service
        self.service_create_manager = service_create_manager
        self.service_deactivate_manager = service_deactivate_manager
        self.service_edit_manager = service_edit_manager
        self.admin_keyboard = admin_keyboard

    async def start(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        await self.user_service.get_user(user_id)
        return MESSAGE["start"], self.admin_keyboard.manage_services()
