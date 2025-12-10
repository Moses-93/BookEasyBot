from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    service = State()
    date = State()
    time = State()
    master = State()
    reminder_offset = State()


class CancelBooking(StatesGroup):
    booking = State()
