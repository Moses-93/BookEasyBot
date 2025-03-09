import logging
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.services.service_manager import ServiceManager


logger = logging.getLogger(__name__)


class ServiceCommandHandler:
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager

    async def start(self, message: Message, user_id: int):
        msg, keyboard = await self.service_manager.start(user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def start_create_service(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to start create new a service")
        msg = await self.service_manager.service_create_manager.start_create_service(
            state
        )
        await message.answer(text=msg)

    async def start_delete_service(
        self, message: Message, state: FSMContext, user_id: int
    ):
        logger.info("Launch the handler to start delete a service")
        msg, keyboard = (
            await self.service_manager.service_deactivate_manager.start_deactivate_service(
                state, user_id
            )
        )
        await message.answer(text=msg, reply_markup=keyboard)

    async def start_edit_service(
        self, message: Message, state: FSMContext, user_id: int
    ):
        logger.info("Launch the handler to start edit a service")
        msg, keyboard = (
            await self.service_manager.service_edit_manager.start_edit_service(
                state, user_id
            )
        )
        await message.answer(text=msg, reply_markup=keyboard)

    async def set_service_name(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set name to state")
        name = message.text
        msg = await self.service_manager.service_create_manager.set_service_name(
            state, name
        )
        await message.answer(text=msg)

    async def finish_create_service(
        self, message: Message, state: FSMContext, user_id: int
    ):
        logger.info("Launch the handler to finish create new a service")
        price = message.text
        msg = await self.service_manager.service_create_manager.finish_create_service(
            state, price, user_id
        )
        await message.answer(text=msg)

    async def finish_deactivate_service(
        self, callback: CallbackQuery, state: FSMContext, user_id: int
    ):
        logger.info("Launch the handler to finish deactivate service")
        service_id = callback.data
        msg = await self.service_manager.service_deactivate_manager.finish_deactivate_service(
            state, service_id, user_id
        )
        await callback.message.answer(text=msg)

    async def select_field_to_update(self, callback: CallbackQuery, state: FSMContext):
        service_id = callback.data.split(":")[0]
        logger.info(f"Service-id: {service_id}")
        msg, keyboard = (
            await self.service_manager.service_edit_manager.select_field_to_update(
                state, service_id
            )
        )
        await callback.message.answer(text=msg, reply_markup=keyboard)

    async def set_field(self, callback: CallbackQuery, state: FSMContext):
        field = callback.data
        msg = await self.service_manager.service_edit_manager.set_field(state, field)
        await callback.message.answer(text=msg)

    async def finish_update_service(
        self, message: Message, state: FSMContext, user_id: int
    ):
        new_value = message.text
        msg = await self.service_manager.service_edit_manager.finish_update_service(
            state, new_value, user_id
        )
        await message.answer(text=msg)
