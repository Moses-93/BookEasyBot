from aiogram.fsm.state import StatesGroup, State


class DeleteServiceState(StatesGroup):
    service = State()


class CreateServiceState(StatesGroup):
    name = State()
    price = State()


class UpdateServiceState(StatesGroup):
    name = State()
    field = State()
    new_value = State()


class ChoiceMasterState(StatesGroup):
    master = State()
