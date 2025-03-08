from datetime import datetime
from aiogram.fsm.context import FSMContext
from typing import Any, List, Dict, Optional

from keyboards.general import display_data_keyboard
from states.date import CreateDateState, DeleteDateState
from utils.validators import is_valid_date, is_valid_time
from ..api_client import APIClient
from .base_schedule import BaseScheduleService


MESSAGE = {
    "start_create_date": "Почнімо! 🚀 Введіть нову дату у форматі YYYY-MM-DD, і ми все налаштуємо!",
    "start_delete_date": "Окей! 📅 Оберіть дату, яку ви хочете видалити.",
    "add_deactivation_time": "Чудово! 🕒 Тепер вкажіть час, коли дата має автоматично видалитися. Наприклад, якщо ви введете 17:00, дата зникне {date} о 17:00:00.",
    "success_create_date": "Супер! 🎁 Дата: {date} успішно створена! Ваші клієнти вже можуть записуватися!",
    "success_delete_date": "Готово! 🎈 Вказану дату успішно видалено!",
    "invalid_date": "Упс! 😅 Щось пішло не так з датою *{date}*. Спробуймо ще раз!",
    "invalid_time": "Ой-ой! 🕰️ Здається, час *{time}* вказано некоректно. Перевірте його та спробуйте знову!",
}


class DateService(BaseScheduleService):

    def __init__(self, api_client: APIClient):
        super().__init__(api_client)

    async def get_dates(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        dates = await self.get("/schedules/dates/", user_id)
        return dates

    async def create_date(self, user_id: int, data: Dict[str, Any]):
        response = await self.create("/schedules/dates/", user_id, data)
        return response

    async def deactivate_date(self, user_id: int, date_id: int):
        response = await self.deactivate(f"/schedules/dates/{date_id}", user_id)
        return response


class DateManager:
    def __init__(self, date_service: DateService):
        self.date_service = date_service

    async def start_create_date(self, state: FSMContext):
        await state.set_state(CreateDateState.date)
        return MESSAGE["start_create_date"]

    async def add_deactivate_time(self, state: FSMContext, date_str: str):
        if not is_valid_date(date_str):
            return MESSAGE["invalid_date"].format(date=date_str)
        await state.update_data(date=date_str)
        await state.set_state(CreateDateState.deactivation_time)
        return MESSAGE["add_deactivation_time"].format(date=date_str)

    async def create_date(self, state: FSMContext, user_id: int, time_str: str):
        data = await state.get_data()
        date_str = data.get("date")

        if not is_valid_time(time_str, date_str):
            return MESSAGE["invalid_time"].format(time=time_str)

        data["deactivation_time"] = str(
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        )
        await self.date_service.create_date(user_id, data)
        await state.clear()
        return MESSAGE["success_create_date"].format(date=date_str)

    async def start_delete_date(self, state: FSMContext, user_id: int):
        dates = await self.date_service.get_dates(user_id)
        await state.set_state(DeleteDateState.date)
        return MESSAGE["start_delete_date"], display_data_keyboard.date_keyboard(dates)

    async def finish_delete_date(self, state: FSMContext, user_id: int, date_id: int):
        await self.date_service.deactivate_date(user_id, date_id)
        await state.clear()
        return MESSAGE["success_delete_date"]
