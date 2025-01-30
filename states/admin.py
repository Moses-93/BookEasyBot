from aiogram.fsm.state import State, StatesGroup


class SetAdminState(StatesGroup):
    name = State()
    chat_id = State()


class DeleteAdminState(StatesGroup):
    admin_id = State()
