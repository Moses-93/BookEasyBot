from keyboards.admin import AdminKeyboard
from .subscription_service import SubscriptionService
from ..user import UserService


class SubscriptionManager:

    def __init__(
        self,
        subscription_service: SubscriptionService,
        user_service: UserService,
        admin_keyboard: AdminKeyboard,
    ):
        self.subscription_service = subscription_service
        self.user_service = user_service
        self.admin_keyboard = admin_keyboard
