from aiogram.fsm.state import State, StatesGroup


class DeleteDateState(StatesGroup):
    date = State()


class CreateDateState(StatesGroup):
    date = State()
    del_time = State()


class ChoiceMasterDate(StatesGroup):
    master = State()
