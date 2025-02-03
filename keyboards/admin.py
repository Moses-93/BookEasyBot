from aiogram.types import (
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
)
from typing import List, Dict
from .base_keyboard import BaseReplyKeyboard, BaseInlineKeyboard


class AdminReplyKeyboard(BaseReplyKeyboard):

    def admin_main_menu(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="Дати"),
                    KeyboardButton(text="Години"),
                    KeyboardButton(text="Керувати послугами"),
                ],
                [
                    KeyboardButton(text="Керувати контактами"),
                    KeyboardButton(text="Історія записів"),
                ],
            ]
        )

    def manage_dates(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="Додати дату"),
                    KeyboardButton(text="Видалити дату"),
                ],
                [KeyboardButton(text="Доступні дати")],
                [KeyboardButton(text="Назад")],
            ]
        )

    def manage_times(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="Додати час"),
                    KeyboardButton(text="Видалити час"),
                ],
                [KeyboardButton(text="Доступний час")],
                [KeyboardButton(text="Назад")],
            ]
        )

    def manage_services(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="Додати послугу"),
                    KeyboardButton(text="Видалити послугу"),
                ],
                [
                    KeyboardButton(text="Редагувати послугу"),
                    KeyboardButton(text="Доступні послуги"),
                ],
                [KeyboardButton(text="Назад")],
            ]
        )

    # def manage_admins(self) -> ReplyKeyboardMarkup:
    #     return self.create_reply_keyboard(
    #         button_names=[
    #             [
    #                 KeyboardButton(text="Призначити адміністратора"),
    #                 KeyboardButton(text="Видалити адміністратора"),
    #             ],
    #             [KeyboardButton(text="Список адміністраторів")],
    #             [KeyboardButton(text="Назад")],
    #         ]
    #     )

    def manage_contacts(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="Додати інформацію"),
                    KeyboardButton(text="Оновити інформацію"),
                ],
                [
                    KeyboardButton(text="Показати інформацію"),
                ],
                [KeyboardButton(text="Назад")],
            ]
        )


class AdminInlineKeyboard(BaseInlineKeyboard):

    def main_inline_keyboard(
        self, data: List[Dict], name: str, callback: str
    ) -> InlineKeyboardMarkup:
        keyboard = []
        for date in data:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=date.get(name), callback_data=f"{date.get(callback)}"
                    )
                ]
            )
        return self.create_inline_keyboard(keyboard=keyboard)

    def description_or_google_link_or_confirm(self):
        return self.create_inline_keyboard(
            keyboard=[
                [
                    InlineKeyboardButton(
                        text="Додати опис", callback_data="add_description"
                    ),
                    InlineKeyboardButton(
                        text="Додати посилання",
                        callback_data="add_google_link",
                    ),
                ],
                [InlineKeyboardButton(text="Завершити", callback_data="confirm")],
            ]
        )


inline_keyboard = AdminInlineKeyboard()
reply_keyboard = AdminReplyKeyboard()
