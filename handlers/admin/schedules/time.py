import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.time import CreateTimeStates, DeleteTimeStates

from services.schedules.time_service import TimeManager


logger = logging.getLogger(__name__)


class TimeCommandHandler:
    def __init__(self, time_manager: TimeManager):
        self.time_manager = time_manager
        self.router = Router()

    async def start_create_time(
        self, message: Message, state: FSMContext, user_id: int
    ):
        logger.info("Launch the handler to create time")
        msg, keyboard = await self.time_manager.start_create_time(state, user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def add_time(self, callback: CallbackQuery, state: FSMContext):
        date_id, date_str = callback.data.split(":")
        msg = await self.time_manager.add_time(state, date_str, date_id)
        await callback.message.answer(text=msg)

    async def finish_create_time(
        self, message: Message, state: FSMContext, user_id: int
    ):
        time_str = message.text
        msg = await self.time_manager.finish_create_time(state, user_id, time_str)
        await message.answer(text=msg, parse_mode="Markdown")

    async def start_delete_time(
        self, message: Message, state: FSMContext, user_id: int
    ):
        msg, keyboard = await self.time_manager.start_delete_time(state, user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def select_time_to_delete(
        self, callback: CallbackQuery, state: FSMContext, user_id: int
    ):
        date_id = callback.data
        msg, keyboard = await self.time_manager.select_time_to_delete(
            state, user_id, date_id
        )
        await callback.message.answer(text=msg, reply_markup=keyboard)

    async def finish_delete_time(
        self, callback: CallbackQuery, state: FSMContext, user_id: int
    ):
        time_id, _ = callback.data.split(":", 1)
        msg = await self.time_manager.finish_delete_time(state, user_id, time_id)
        await callback.message.answer(text=msg)
