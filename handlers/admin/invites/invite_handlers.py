import logging
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from services.invites import InviteManager

logger = logging.getLogger(__name__)


class InviteCommandHandler:
    def __init__(self, invite_manager: InviteManager):
        self.invite_manager = invite_manager

    async def start(self, message: Message, user_id: int):
        msg, keyboard = await self.invite_manager.start(user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def invite_to_client(self, message: Message, user_id: int):
        msg = await self.invite_manager.create_invite_to_client(user_id)
        await message.answer(text=msg, parse_mode="Markdown")
