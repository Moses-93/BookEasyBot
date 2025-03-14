from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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
                    KeyboardButton(text="📔 Контакти"),
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
                    KeyboardButton(text="❌ Видалити послугу"),
                ],
                [
                    KeyboardButton(text="🔄 Оновити послугу"),
                    KeyboardButton(text="📋 Доступні послуги"),
                ],
                [KeyboardButton(text="🔙 Назад")],
            ]
        )

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

    def manage_subscriptions(
        self,
        has_active_subscription: bool,
        is_subscription_expiring: bool,
    ):
        keyboard = ReplyKeyboardBuilder()

        if not has_active_subscription:
            keyboard.add(KeyboardButton(text="🆓 Спробувати безкоштовно"))
        else:
            keyboard.add(
                KeyboardButton(text="📜 Моя підписка"),
                KeyboardButton(text="❌ Скасувати підписку"),
            )
            if is_subscription_expiring:
                keyboard.add(KeyboardButton(text="🔄 Оновити підписку"))

        keyboard.add(KeyboardButton(text="💳 Придбати підписку"))

        keyboard.adjust(2)

        keyboard.row(KeyboardButton(text="🔙 Назад"))

        return keyboard.as_markup(resize_keyboard=True)

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
