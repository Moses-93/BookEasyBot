from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from .base_keyboard import BaseReplyKeyboard


class AdminKeyboard(BaseReplyKeyboard):

    def admin_main_menu(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📖 Послуги"),
                    KeyboardButton(text="📒 Записи"),
                    KeyboardButton(text="📅 Розклад"),
                ],
                [
                    KeyboardButton(text="📕 Контакти"),
                    KeyboardButton(text="📊 Аналітика"),
                    KeyboardButton(text="⭐️ Відгуки"),
                ],
                [
                    KeyboardButton(text="⚙️ Налаштування"),
                    KeyboardButton(text="☎️ Підтримка"),
                ],
            ]
        )

    def manage_settings(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="💳 Підписка"),
                    KeyboardButton(text="📤 Запрошення та посилання"),
                ],
                [
                    KeyboardButton(text="🎁 Програма лояльності"),
                ],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

    def manage_schedule(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="➕📅 Додати дату"),
                    KeyboardButton(text="❌📅 Видалити дату"),
                ],
                [
                    KeyboardButton(text="➕⏰ Додати час"),
                    KeyboardButton(text="❌⏰ Видалити час"),
                ],
                [
                    KeyboardButton(text="📅 Доступні дати"),
                    KeyboardButton(text="⏱️ Доступний час"),
                ],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

    def manage_services(self) -> ReplyKeyboardMarkup:
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="➕ Додати послугу"),
                    KeyboardButton(text="➖ Видалити послугу"),
                ],
                [
                    KeyboardButton(
                        text="✏️ Редагувати послугу"
                    ),  # Олівець для редагування
                    KeyboardButton(text="📋 Доступні послуги"),
                ],
                [KeyboardButton(text="🔙 Назад")],
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

    def manage_statistics(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📈 Кількість записів"),
                    KeyboardButton(text="⭐️ Популярні послуги"),
                ],
                [KeyboardButton(text="💰 Дохід")],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

    def manage_subscriptions(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="💳 Отримати підписку"),
                    KeyboardButton(text="🆓 Спробувати безкоштовно"),
                ],
                [
                    KeyboardButton(text="📜 Моя підписка"),
                    KeyboardButton(text="❌ Скасувати підписку"),
                ],
                [
                    KeyboardButton(text="🔙 Назад"),
                ],
            ]
        )

    def manage_referrals(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="📲 Посилання для клієнтів"),
                    KeyboardButton(text="🤝 Запросити колегу"),
                ],
                [KeyboardButton(text="👥 Запрошені майстри")],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

    def manage_loyalty_program(self):
        return self.create_reply_keyboard(
            keyboard=[
                [
                    KeyboardButton(text="🛠 Створити промокод"),
                    KeyboardButton(text="📜 Мої промокоди"),
                ],
                [
                    KeyboardButton(text="⚙️ Налаштувати знижку"),
                    KeyboardButton(text="📊 Статистика використання"),
                ],
                [
                    KeyboardButton(text="🔙 Назад"),
                ],
            ]
        )


admin_keyboard = AdminKeyboard()
