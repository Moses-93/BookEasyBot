from aiogram.types import InlineKeyboardMarkup
from typing import Tuple

from keyboards.admin import AdminKeyboard
from services.user import UserService
from services.invites.invite_service import InviteService


MESSAGE = {
    "Invitations_and_links": "Ви перейшли в розділ керування посиланнями та запрошеннями.\nТут ви можете створити посилання клієнтам для запису.\nА незабаром тут буде доданий дуже цікавий та корисний функціонал!",
    "create_link_successfully": "Надайте це посилання вашим клієнтам:\n\n`{link}`\n\nЗа ним вони зможуть здійснити запис саме до вас!",
}


class InviteManager:
    def __init__(
        self,
        invite_service: InviteService,
        user_service: UserService,
        admin_keyboard: AdminKeyboard,
    ):
        self.invite_service = invite_service
        self.user_service = user_service
        self.admin_keyboard = admin_keyboard

    async def start(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        await self.user_service.get_user(user_id)
        return MESSAGE["Invitations_and_links"], self.admin_keyboard.manage_invites()

    async def create_invite_to_client(self, user_id: int) -> str:
        invite_to_client = await self.invite_service.create_link_to_client(user_id)
        return MESSAGE["create_link_successfully"].format(link=invite_to_client)
