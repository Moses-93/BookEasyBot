from aiogram.fsm.state import State, StatesGroup


class CreateFeedbackState(StatesGroup):
    rating = State()
    comment = State()
