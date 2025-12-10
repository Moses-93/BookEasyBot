import re
import logging

from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def is_valid_price(price: str) -> bool:
    try:
        price_int = int(price)
        if price_int <= 0:
            logger.warning(
                f"The user input invalid price: {price} | type: {type(price)}"
            )
            return False
    except ValueError:
        return False
    return True


def is_valid_date(date: str) -> bool:
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", date):
        logger.warning(f"The user entered the invalid date format: {date}")
        return False

    logger.info(f"date: {date}")

    date = datetime.strptime(date, "%Y-%m-%d").date()
    current_time = datetime.now()

    if date < current_time.date():
        logger.warning(f"The user has entered an expired date: {date}")
        return False
    return True


def is_valid_time(time_str, date_str: Optional[str]) -> bool:
    time_pattern = r"^([01]?[0-9]|2[0-3]):([0-5][0-9])$"

    if not re.match(time_pattern, time_str):
        logger.warning(f"The user entered the invalid time format: {time_str}")
        return False

    if date_str:
        try:
            input_datetime = datetime.strptime(
                f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
            )
            if input_datetime < datetime.now():
                logger.warning(f"The user entered the past time: {date_str} {time_str}")
                return False
        except ValueError:
            return False

    return True


def validate_phone(phone_number: str):
    PHONE_REGEX = r"^\+380\d{9}$"
    if not re.match(PHONE_REGEX, phone_number):
        return False
    return True
