from aiogram import F, Router
from .subscription_handlers import SubscriptionCommandHandler


class SubscriptionRouter:

    def __init__(self, subscription_command_handler: SubscriptionCommandHandler):
        self.router = Router()
        self._register_handlers(subscription_command_handler)

    def _register_handlers(self, handler: SubscriptionCommandHandler):
        """Реєстрація обробників."""
        self.router.message.register(handler.start, F.text == "💳 Підписка")
        self.router.message.register(
            handler.buy_subscription, F.text == "💳 Придбати підписку"
        )
        self.router.message.register(
            handler.active_free_subscription, F.text == "🆓 Спробувати безкоштовно"
        )
        self.router.message.register(
            handler.show_user_subscription, F.text == "📜 Моя підписка"
        )
        self.router.message.register(
            handler.cancel_user_subscription, F.text == "❌ Скасувати підписку"
        )
