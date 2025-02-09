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
                    KeyboardButton(text="📋 Послуги"),
                    KeyboardButton(text="📖 Записи"),
                    KeyboardButton(text="📅 Розклад"),
                ],
                [
                    KeyboardButton(text="📕 Контакти"),
                    KeyboardButton(text="📊 Статистика"),
                    KeyboardButton(text="⭐️ Відгуки"),
                ],
                [
                    KeyboardButton(text="💳 Підписка"),
                    KeyboardButton(text="☎️ Підтримка"),
                ],
            ]
        )

    def manage_schedule(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="➕ Додати дату"),
                    KeyboardButton(text="➖ Видалити дату"),
                ],
                [
                    KeyboardButton(text="⏰ Додати час"),
                    KeyboardButton(text="❌ Видалити час"),
                ],
                [
                    KeyboardButton(text="📅 Доступні дати"),
                    KeyboardButton(text="⏱️ Доступний час"),
                ],
            ]
        )

    def manage_services(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="➕ Додати послугу"),  # Додавання
                    KeyboardButton(text="➖ Видалити послугу"),  # Видалення
                ],
                [
                    KeyboardButton(
                        text="✏️ Редагувати послугу"
                    ),  # Олівець для редагування
                    KeyboardButton(text="📋 Доступні послуги"),  # Список
                ],
                [KeyboardButton(text="🔙 Назад")],  # Назад
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
                    KeyboardButton(text="➕ Додати дані"),
                    KeyboardButton(text="🔄 Оновити дані"),
                ],
                [
                    KeyboardButton(text="📖 Показати дані"),
                ],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

    def manage_bookings(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📂 Активні записи"),
                    KeyboardButton(text="🗄️ Архів записів"),
                ],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

    def manage_statistics(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📈 Кількість записів"),  # Графік зростання
                    KeyboardButton(
                        text="⭐️ Популярні послуги"
                    ),  # Зірка для топ-записів
                ],
                [KeyboardButton(text="💰 Дохід")],  # Гроші для доходу
                [KeyboardButton(text="🔙 Назад")],  # Назад
            ]
        )

    def manage_subscriptions(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📜 Моя підписка"),  # Рулон паперу для статусу
                    KeyboardButton(text="🔄 Оновити підписку"),  # Стрілки для оновлення
                ],
                [KeyboardButton(text="❌ Скасувати підписку")],  # Хрестик для видалення
                [KeyboardButton(text="🔙 Назад")],  # Назад
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
