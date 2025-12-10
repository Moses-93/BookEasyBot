import logging
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from typing import Any, List, Dict, Optional, Tuple

from keyboards.general import display_data_keyboard
from states.time import CreateTimeStates, DeleteTimeStates
from utils.validators import is_valid_time
from ..api_client import APIClient
from .base_schedule import BaseScheduleService
from .date_service import DateService


MESSAGE = {
    "start_create_time": "Почнімо! 🕒 Оберіть дату, до якої хочете додати новий час.",
    "start_delete_time": "Поїхали! 🗑️ Оберіть дату, з якої потрібно видалити час.",
    "select_date": "Чудово! 🎯 Тепер вкажіть час у форматі HH:MM.",
    "finish_create_time": "Вітаю! 🎉 Час {time} успішно створений і вже готовий для запису клієнтів!",
    "select_delete_time": "Оберіть зі списку час, який бажаєте прибрати.",
    "finish_delete_time": "Готово! ✅ Час успішно видалений.",
    "invalid_time": "Упс! 🕒 Щось не так з часом *{time}*. Давайте спробуємо ще раз!",
}

logger = logging.getLogger(__name__)


class TimeService(BaseScheduleService):

    def __init__(self, http_client: APIClient):
        super().__init__(http_client)

    async def create_time(self, user_id: int, data: Dict[str, Any]):
        return await self.create("/schedules/dates/times/", user_id, data)

    async def deactivate_time(self, user_id: int, time_id: int):
        await self.deactivate(f"/schedules/dates/times/{time_id}", user_id)

    async def get_times(self, user_id: int):
        return await self.get("/schedules/dates/times/", user_id)


class TimeManager:

    def __init__(self, time_service: TimeService, date_service: DateService):
        self.time_service = time_service
        self.date_service = date_service

    async def start_create_time(
        self, state: FSMContext, user_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        logger.info(f"Launch the method to create time")
        dates = await self.date_service.get_dates(user_id)
        msg = MESSAGE["start_create_time"]
        keyboard = display_data_keyboard.date_keyboard(dates)
        logger.info(f"keyboard: {keyboard}")
        await state.set_state(CreateTimeStates.date)
        return msg, keyboard

    async def add_time(self, state: FSMContext, date_str: str, date_id: int) -> str:
        logger.info(f"Launch the method to add time to state")
        await state.set_state(CreateTimeStates.time)
        await state.update_data(date_id=date_id, date=date_str)
        msg = MESSAGE["select_date"]
        return msg

    async def finish_create_time(
        self, state: FSMContext, user_id: int, time_str: str
    ) -> str:
        logger.info(f"Launch the method to finish create  time")
        date_str = await state.get_value("date")
        if not is_valid_time(time_str, date_str):
            return MESSAGE["invalid_time"].format(time=time_str)
        await state.update_data(time=time_str)
        data = await state.get_data()
        logger.info(f"Data: {data}")
        created_time = await self.time_service.create_time(user_id, data)
        await state.clear()
        return MESSAGE["finish_create_time"].format(time=created_time["time"])

    async def start_delete_time(
        self,
        state: FSMContext,
        user_id: int,
    ) -> Tuple[str, InlineKeyboardMarkup]:
        logger.info(f"Launch the method to starting delete time")
        dates = await self.date_service.get_dates(user_id)
        await state.set_state(DeleteTimeStates.date)
        return MESSAGE["start_delete_time"], display_data_keyboard.date_keyboard(dates)

    async def select_time_to_delete(
        self, state: FSMContext, user_id: int, date_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        logger.info(f"Launch the method to choose the time of deletion")
        await state.update_data(date_id=date_id)
        times = await self.time_service.get_times(user_id)
        await state.set_state(DeleteTimeStates.time)
        return MESSAGE["select_delete_time"], display_data_keyboard.time_keyboard(times)

    async def finish_delete_time(
        self, state: FSMContext, user_id: int, time_id: int
    ) -> str:
        logger.info(f"Run the method to complete the time deletion")
        await self.time_service.deactivate_time(user_id, time_id)
        await state.clear()
        return MESSAGE["finish_delete_time"]
