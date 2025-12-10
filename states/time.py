from aiogram.fsm.state import State, StatesGroup


class CreateTimeStates(StatesGroup):
    date = State()
    time = State()


class DeleteTimeStates(StatesGroup):
    date = State()
    time = State()


class ShowTimeStates(StatesGroup):
    date = State()
    time = State()


class ChoiceMasterTime(StatesGroup):
    master = State()
