import logging
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.schedules.date_service import DateManager


logger = logging.getLogger(__name__)


class DateCommandHandler:
    def __init__(self, date_manager: DateManager):
        self.date_manager = date_manager

    async def start(self, message: Message, user_id: int):
        msg, keyboard = await self.date_manager.start(user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def start_create_date(self, message: Message, state: FSMContext):
        msg = await self.date_manager.start_create_date(state)
        await message.answer(text=msg)

    async def start_delete_date(
        self, message: Message, state: FSMContext, user_id: int
    ):
        logger.info("Starting delete date")
        msg, keyboard = await self.date_manager.start_delete_date(state, user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def add_deactivate_time(self, message: Message, state: FSMContext):
        date = message.text
        msg = await self.date_manager.add_deactivate_time(state, date)
        await message.answer(text=msg, parse_mode="Markdown")

    async def finish_create_date(
        self, message: Message, state: FSMContext, user_id: int
    ):
        time = message.text
        msg = await self.date_manager.create_date(state, user_id, time)
        await message.answer(text=msg, parse_mode="Markdown")

    async def finish_delete_date(
        self, callback: CallbackQuery, state: FSMContext, user_id: int
    ):
        date_id = callback.data.split(":")[0]
        msg = await self.date_manager.finish_delete_date(state, user_id, date_id)
        await callback.message.answer(text=msg)
