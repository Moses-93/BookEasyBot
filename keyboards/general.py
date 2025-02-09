from aiogram.types import KeyboardButton, InlineKeyboardButton
from .base_keyboard import BaseReplyKeyboard, BaseInlineKeyboard
from typing import List, Dict


class GeneralReplyKeyboard(BaseReplyKeyboard):

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


class DynamicKeyboard(BaseInlineKeyboard, BaseReplyKeyboard):

    def dynamic_inline_keyboard(self, button_names: Dict):
        keyboard = []
        for name, callback in button_names.items():
            keyboard.append([InlineKeyboardButton(text=name, callback_data=callback)])
        return self.create_inline_keyboard(keyboard=keyboard)

    def dynamic_reply_keyboard(self, button_names: List[str | int]):
        keyboard = []
        for name in button_names:
            keyboard.append([KeyboardButton(text=name)])
        return self.create_reply_keyboard(keyboard=keyboard)


general_reply_keyboard = GeneralReplyKeyboard()
dynamic_keyboard = DynamicKeyboard()
