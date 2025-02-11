import logging
from aiogram.types import KeyboardButton
from .base_keyboard import BaseReplyKeyboard


logger = logging.getLogger(__name__)


class UserKeyboard(BaseReplyKeyboard):

    def main_keyboard(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📝 Новий запис"),
                ],
                [
                    KeyboardButton(text="📋 Послуги"),
                    KeyboardButton(text="🗓 Розклад"),
                    KeyboardButton(text="📖 Мої записи"),
                ],
                [
                    KeyboardButton(text="⭐️ Відгуки"),
                    KeyboardButton(text="📕 Контакти"),
                    KeyboardButton(text="☎️ Підтримка"),
                ],
            ]
        )

    def manage_bookings(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📂 Активні записи"),
                    KeyboardButton(text="🗄️ Архів записів"),
                ],
                [KeyboardButton(text="❌ Скасувати запис")],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )


user_keyboard = UserKeyboard()
