import logging
from aiogram.fsm.context import FSMContext
from typing import Union
from keyboards import AdminKeyboard, UserKeyboard


logger = logging.getLogger(__name__)


class NavigationManager:
    def __init__(self, keyboard: Union[AdminKeyboard, UserKeyboard]):
        self.keyboard = keyboard
        self.history = {}

    async def go_to(self, user_id: int, state: FSMContext, new_section: str):
        """Moves to a new section, adding it to the history"""
        await state.clear()

        self.history.setdefault(user_id, ["main_menu"]).append(new_section)

        logger.info(
            f"User navigated to {new_section}. History: {self.history[user_id]}"
        )
        logger.info(f"History after: {self.history}")

    async def go_back(self, user_id: int, state: FSMContext):
        """Returns the user to the previous section"""
        await state.clear()

        if user_id not in self.history or len(self.history[user_id]) <= 1:
            return self.keyboard.main_menu()

        logger.info(f"User navigation history: {self.history[user_id]}")

        self.history[user_id].pop()
        preview_section = self.history[user_id][-1]

        logger.info(f"The user {user_id} is back in the section: {preview_section}")

        return getattr(self.keyboard, preview_section, self.keyboard.main_menu)()
