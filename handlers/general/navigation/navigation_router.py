from typing import List
from aiogram import Router, F
from handlers.general.navigation import NavigationCommandHandler


class NavigationRouter:

    def __init__(
        self, navigation_command_handler: NavigationCommandHandler, sections: List[str]
    ):
        self.router = Router()
        self._sections = sections
        self._register_handlers(navigation_command_handler)

    def _register_handlers(self, handler: NavigationCommandHandler):
        """Реєстрація обробників."""
        self.router.message.register(handler.to_go, F.text.in_(self._sections))
        self.router.message.register(handler.back_button, F.text == "🔙 Назад")
