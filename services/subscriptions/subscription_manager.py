import logging
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional, Tuple, Union

from keyboards.admin import AdminKeyboard
from .subscription_service import SubscriptionService
from ..user import UserService


MESSAGE = {
    "start": "🌟 Ви перейшли в розділ підписки! Тут ви можете активувати нову підписку, оновити поточну або скасувати її. Давайте разом налаштуємо ваш доступ!",
    "activated_free_subscription": "🎉 Вітаю! Ваша пробна підписка активована. Тепер ви можете отримувати записи від користувачів та керувати ними!",
    "update_subscription": "🔄 Час оновити підписку! Продовжуйте приймати записи без обмежень.\nДля оплати просто натисніть кнопку нижче ⬇️",
    "refund_money": "😢 Нам прикро, що ви вирішили скасувати підписку.\n\n"
    "🔹 Якщо ви скасовуєте підписку протягом 14 днів після оплати, вам повернеться вся сума коштів.\n"
    "🔹 Якщо ви користувалися підпискою більше 14 днів, вам буде повернено частину коштів.\n"
    "Сума до повернення: *{amount}* грн.\n\n"
    "Ви впевнені, що хочете скасувати підписку?",
    "no_subscription": "🤔 Здається, у вас ще немає активної підписки, тому скасувати нічого. Можливо, саме час її активувати? 😊",
    "trial_already_used": "🙂 На жаль, ви вже використали свою **пробну підписку**. Її можна активувати лише один раз.\nАле ви можете оформити повноцінну підписку та продовжувати отримувати запити від клієнтів! 🚀",
}

logger = logging.getLogger(__name__)


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

    async def start(self, user_id: int) -> Optional[Tuple[str, InlineKeyboardMarkup]]:
        await self.user_service.get_user(user_id)
        subscription = await self.subscription_service.get_user_subscription(user_id)
        end_date = datetime.fromisoformat(subscription["end_date"])
        is_subscription_expiring = self.subscription_service.is_subscription_expiring(
            end_date
        )
        return MESSAGE["start"], self.admin_keyboard.manage_subscriptions(
            subscription, is_subscription_expiring
        )

    def create_payment_button(self, payment_url: str) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="🛒 Оплатити", url=payment_url)
        return keyboard.as_markup()

    def create_cancel_subscription_button(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        keyboard.button(
            text="❌ Підтвердити скасування", callback_data="confirm_cancel_sub"
        )
        return keyboard.as_markup()

    async def create_payment_link(
        self, user_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        subscription_plan = await self.subscription_service.get_subscription_plan(
            user_id
        )
        payment_url = await self.subscription_service.get_payment_url(
            subscription_plan["id"], subscription_plan["price"], user_id
        )

        return self.subscription_service.format_plan(
            subscription_plan
        ), self.create_payment_button(payment_url)

    async def update_user_subscription(
        self, user_id: int
    ) -> Tuple[str, InlineKeyboardMarkup]:
        subscription_plan = await self.subscription_service.get_subscription_plan(
            user_id
        )
        payment_url = await self.subscription_service.get_payment_url(
            subscription_plan["id"], subscription_plan["price"], user_id
        )
        return MESSAGE["update_subscription"], self.create_payment_button(payment_url)

    async def active_free_subscription(self, user_id: int) -> str:
        activated_free_sub = await self.subscription_service.activate_free_subscription(
            user_id
        )
        if not activated_free_sub:
            return MESSAGE["trial_already_used"]
        return MESSAGE["activated_free_subscription"]

    async def cancel_user_subscription(
        self, user_id: int
    ) -> Union[Tuple[str, None], Tuple[str, InlineKeyboardMarkup]]:
        detail_subscription = await self.subscription_service.cancel_user_subscription(
            user_id
        )
        if not detail_subscription["has_subscription"]:
            return MESSAGE["no_subscription"], None
        return (
            MESSAGE["refund_money"].format(amount=detail_subscription["refund_amount"]),
            self.create_cancel_subscription_button(),
        )

    async def show_user_subscription(self, user_id: int) -> str:
        user_subscription = await self.subscription_service.get_user_subscription(
            user_id
        )
        return self.subscription_service.format_subscription(user_subscription)
