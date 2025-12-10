import logging
from typing import List, Union
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logger = logging.getLogger(__name__)


class BaseReplyKeyboard:
    def create_reply_keyboard(
        self,
        keyboard: List[List[Union[KeyboardButton]]],
        resize_keyboard: bool = True,
        one_time_keyboard: bool = False,
    ) -> ReplyKeyboardMarkup:
        """
        Створює ReplyKeyboardMarkup з кнопок.
        :param keyboard: Список назв кнопок або словників з параметрами кнопок.
        :param resize_keyboard: Чи потрібно стискати клавіатуру.
        :param one_time_keyboard: Чи має клавіатура зникнути після натискання.
        """

        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard,
        )


class BaseInlineKeyboard:

    def create_inline_keyboard(
        self, keyboard: List[List[Union[InlineKeyboardButton]]]
    ) -> InlineKeyboardMarkup:
        """
        Створює InlineKeyboardMarkup з кнопок.
        :param keyboard: Словник {текст кнопки: callback_data}.
        """

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
