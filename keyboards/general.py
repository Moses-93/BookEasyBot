from typing import List, Dict, Callable, Optional
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from .base_keyboard import BaseReplyKeyboard, BaseInlineKeyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from utils.formatted_view import sorted_data


class Paginator:
    def __init__(self, offset: int = 0, limit: int = 5):
        self.offset = offset
        self.limit = limit

    def pagination_keyboard(
        self, has_more: bool, callback_prefix: str
    ) -> InlineKeyboardMarkup:
        """Генерує клавіатуру для пагінації"""
        keyboard = InlineKeyboardBuilder()

        if self.offset > 0:
            keyboard.button(
                text="⬅️ Назад",
                callback_data=f"{callback_prefix}:prev:{self.offset - self.limit}:{self.limit}",
            )
        if has_more:
            keyboard.button(
                text="Вперед ➡️",
                callback_data=f"{callback_prefix}:next:{self.offset + self.limit}:{self.limit}",
            )

        return keyboard.as_markup()


class DynamicKeyboard(BaseInlineKeyboard, BaseReplyKeyboard):

    def dynamic_inline_keyboard(self, button_names: Dict):
        keyboard = []
        for name, callback in button_names.items():
            keyboard.append([InlineKeyboardButton(text=name, callback_data=callback)])
        return self.create_inline_keyboard(keyboard=keyboard)

    def dynamic_reply_keyboard(self, button_names: List[str]):
        keyboard = []
        for name in button_names:
            keyboard.append([KeyboardButton(text=name)])
        return self.create_reply_keyboard(keyboard=keyboard)


class DisplayDataKeyboard(BaseInlineKeyboard):
    def generate_keyboard(
        self,
        data: List[Dict],
        text_key: str,
        callback_key: List,
        preprocess: Optional[Callable[[List[Dict]], List[Dict]]] = None,
    ):
        """
        Універсальний метод для створення клавіатур.

        :param data: Список словників з даними для клавіатури
        :param text_key: Ключ у словнику, який використовується для тексту кнопки
        :param callback_key: Ключ у словнику для callback_data
        :param preprocess: Функція для попередньої обробки даних (наприклад, сортування)
        :return: InlineKeyboardMarkup
        """
        if preprocess:
            data = preprocess(data)

        keyboard = [
            [
                InlineKeyboardButton(
                    text=i[text_key],
                    callback_data=f"{i[callback_key[0]]}:{i[callback_key[1]]}",
                )
            ]
            for i in data
        ]
        return self.create_inline_keyboard(keyboard=keyboard)

    def service_keyboard(self, services: List[Dict]):
        return self.generate_keyboard(
            services,
            text_key="name",
            callback_key=["id", "name"],
            preprocess=sorted_data,
        )

    def date_keyboard(self, dates: List[Dict]):
        return self.generate_keyboard(
            dates, text_key="date", callback_key=["id", "date"], preprocess=sorted_data
        )

    def time_keyboard(self, times: List[Dict]):
        return self.generate_keyboard(
            times, text_key="time", callback_key=["id", "time"], preprocess=sorted_data
        )

    def booking_keyboard(self):
        return self.create_inline_keyboard(
            buttons=[
                [InlineKeyboardButton(text="Всі записи", callback_data="all_bookings")],
                [
                    InlineKeyboardButton(
                        text="Активні записи", callback_data="active_bookings"
                    )
                ],
            ]
        )

    def choice_master(self, data: dict[dict[List[Dict]]]):
        """Створення клавіатури для вибору майстра."""
        masters = data.get("detail").get("masters")
        return self.generate_keyboard(
            masters, text_key="name", callback_key="id", preprocess=sorted_data
        )


class ManageBooking:
    def manage_bookings(self, is_master: bool = False):
        keyboard = ReplyKeyboardBuilder()

        keyboard.add(
            KeyboardButton(text="📂 Активні записи"),
            KeyboardButton(text="🗄️ Архів записів"),
        )

        if not is_master:
            keyboard.add(KeyboardButton(text="❌ Скасувати запис"))

        keyboard.add(KeyboardButton(text="⬅️ Назад"))

        keyboard.adjust(2, 1 if is_master else 1, 1)

        return keyboard.as_markup(resize_keyboard=True)


class RequestContact(BaseReplyKeyboard):
    def request_phone(self):

        contact_button = KeyboardButton(
            text="📞 Поділитися номером", request_contact=True
        )
        return self.create_reply_keyboard([[contact_button]])


request_contact = RequestContact()
manage_booking_keyboard = ManageBooking()
display_data_keyboard = DisplayDataKeyboard()
dynamic_keyboard = DynamicKeyboard()
