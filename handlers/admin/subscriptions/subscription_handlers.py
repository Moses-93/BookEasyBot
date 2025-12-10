import logging
from aiogram.types import Message, CallbackQuery
from services.subscriptions.subscription_manager import SubscriptionManager


logger = logging.getLogger(__name__)


class SubscriptionCommandHandler:

    def __init__(self, subscription_manager: SubscriptionManager):
        self.subscription_manager = subscription_manager

    async def start(self, message: Message, user_id: int):
        msg, keyboard = await self.subscription_manager.start(user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def buy_subscription(self, message: Message, user_id: int):
        msg, keyboard = await self.subscription_manager.create_payment_link(user_id)
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def cancel_user_subscription(self, message: Message, user_id: int):
        msg, keyboard = await self.subscription_manager.cancel_user_subscription(
            user_id
        )
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def update_user_subscription(self, message: Message, user_id: int):
        msg, keyboard = await self.subscription_manager.update_user_subscription(
            user_id
        )
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def active_free_subscription(self, message: Message, user_id: int):
        msg = await self.subscription_manager.active_free_subscription(user_id)
        await message.answer(text=msg)

    async def show_user_subscription(self, message: Message, user_id: int):
        msg = await self.subscription_manager.show_user_subscription(user_id)
        await message.answer(text=msg, parse_mode="Markdown")
