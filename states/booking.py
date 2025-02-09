from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    service = State()
    date = State()
    time = State()
    master = State()
    reminter_ofset = State()


class CancelBook(StatesGroup):
    book = State()
