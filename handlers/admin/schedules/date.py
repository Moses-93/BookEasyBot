import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.date import DeleteDateState, CreateDateState
from services.schedules.date_service import DateManager


logger = logging.getLogger(__name__)
router = Router()


class CommandHandler:
    def __init__(self, date_manager: DateManager, router: Router):
        self.date_manager = date_manager
        self.router = router
        self._register_handlers()

    def _register_handlers(self):
        """Реєстрація обробників."""
        self.router.message.register(
            self.start_create_date, F.text == "➕📅 Додати дату"
        )
        self.router.message.register(
            self.start_delete_date, F.text == "❌📅 Видалити дату"
        )
        self.router.message.register(self.add_deactivate_time, CreateDateState.date)
        self.router.message.register(
            self.finish_create_date, CreateDateState.deactivation_time
        )
        self.router.callback_query.register(
            self.finish_delete_date, DeleteDateState.date
        )

    async def start_create_date(self, message: Message, state: FSMContext):
        msg = await self.date_manager.start_create_date(state)
        await message.answer(text=msg)

    async def start_delete_date(
        self, message: Message, state: FSMContext, user_id: int
    ):
        logger.info("Starting delete date")
        msg, keyboard = await self.date_manager.start_delete_date(state, user_id)
        logger.info(
            f"msg: {msg} | type: {type(msg)} keyboard: {keyboard} | type: {type(keyboard)}"
        )
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


def setup_date_handlers(router: Router, date_manager: DateManager):
    CommandHandler(date_manager, router)
