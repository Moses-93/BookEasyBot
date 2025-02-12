from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    phone_number = State()
