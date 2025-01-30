from typing import List, Dict, Callable, Optional
from aiogram.types import InlineKeyboardButton

from .base_keyboard import BaseInlineKeyboard
from utils.formatted_view import sorted_data


class BookingKeyboard(BaseInlineKeyboard):
    def generate_keyboard(
        self,
        data: List[Dict],
        text_key: str,
        callback_key: str,
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
                    text=item[text_key], callback_data=f"{item[callback_key]}"
                )
            ]
            for item in data
        ]
        return self.create_inline_keyboard(keyboard=keyboard)

    def service_keyboard(self, services: List[Dict]):
        return self.generate_keyboard(
            services, text_key="name", callback_key="id", preprocess=sorted_data
        )

    def date_keyboard(self, dates: List[Dict]):
        return self.generate_keyboard(
            dates, text_key="date", callback_key="id", preprocess=sorted_data
        )

    def time_keyboard(self, times: List[Dict]):
        return self.generate_keyboard(
            times, text_key="time", callback_key="id", preprocess=sorted_data
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

    def reminder_keyboard(self):
        return self.create_inline_keyboard(
            buttons=[
                [
                    InlineKeyboardButton(
                        text="Нагадати про запис", callback_data="reminder_button"
                    )
                ],
            ]
        )

    def cancel_booking(self):
        return self.create_inline_keyboard(
            buttons=[
                [
                    InlineKeyboardButton(
                        text="Скасувати запис", callback_data="cancel_booking"
                    )
                ],
            ]
        )


booking_keyboard = BookingKeyboard()
