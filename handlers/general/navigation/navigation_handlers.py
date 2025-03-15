from typing import Dict
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.navigation import NavigationManager


class NavigationCommandHandler:

    def __init__(self, navigation_manager: NavigationManager, sections: Dict[str, str]):
        self.navigation_manager = navigation_manager
        self._sections = sections

    async def to_go(self, message: Message, state: FSMContext, user_id: int):
        button = message.text
        section = self._sections.get(button)
        await self.navigation_manager.go_to(user_id, state, section)

    async def back_button(self, message: Message, state: FSMContext, user_id: int):
        keyboard = await self.navigation_manager.go_back(user_id, state)
        await message.answer(text=f"Повернення до ...", reply_markup=keyboard)
