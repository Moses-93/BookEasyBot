from aiogram import F, Router
from .subscription_handlers import SubscriptionCommandHandler


class SubscriptionRouter:

    def __init__(self, subscription_command_handler: SubscriptionCommandHandler):
        self.router = Router()
        self._register_handlers(subscription_command_handler)

    def _register_handlers(self, handler: SubscriptionCommandHandler):
        """Реєстрація обробників."""
        pass
