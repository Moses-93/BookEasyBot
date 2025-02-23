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


user_keyboard = UserKeyboard()
