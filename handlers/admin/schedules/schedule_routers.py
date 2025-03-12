from aiogram import F, Router

from states.date import CreateDateState, DeleteDateState
from states.time import CreateTimeStates, DeleteTimeStates
from .date import DateCommandHandler
from .time import TimeCommandHandler


class DateRouter:
    def __init__(self, date_command_handler: DateCommandHandler):
        self.router = Router()
        self._register_handlers(date_command_handler)

    def _register_handlers(self, handler: DateCommandHandler):
        """Реєстрація обробників."""
        self.router.message.register(
            handler.start_create_date, F.text == "➕📅 Додати дату"
        )
        self.router.message.register(
            handler.start_delete_date, F.text == "❌📅 Видалити дату"
        )
        self.router.message.register(handler.add_deactivate_time, CreateDateState.date)
        self.router.message.register(
            handler.finish_create_date, CreateDateState.deactivation_time
        )
        self.router.callback_query.register(
            handler.finish_delete_date, DeleteDateState.date
        )


class TimeRouter:
    def __init__(self, time_command_handler: TimeCommandHandler):
        self.router = Router()
        self._register_handlers(time_command_handler)

    def _register_handlers(self, handler: TimeCommandHandler):
        self.router.message.register(
            handler.start_create_time, F.text == "➕⏰ Додати час"
        )
        self.router.message.register(
            handler.start_delete_time, F.text == "❌⏰ Видалити час"
        )
        self.router.callback_query.register(handler.add_time, CreateTimeStates.date)
        self.router.message.register(handler.finish_create_time, CreateTimeStates.time)
        self.router.callback_query.register(
            handler.select_time_to_delete, DeleteTimeStates.date
        )
        self.router.callback_query.register(
            handler.finish_delete_time, DeleteTimeStates.time
        )
