from aiogram.fsm.state import State, StatesGroup


class CreateBusinessInfoState(StatesGroup):
    name = State()
    address = State()
    phone = State()
    working_hours = State()
    google_link = State()
    description = State()


class UpdateBusinessInfoState(StatesGroup):
    field = State()
    new_value = State()


class ChoiceMasterState(StatesGroup):
    master = State()