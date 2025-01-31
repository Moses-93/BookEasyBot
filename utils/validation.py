import re
import logging

from datetime import datetime, timedelta, time

logger = logging.getLogger(__name__)


def validate_price(price: str):
    try:
        price = int(price)
    except ValueError:
        return "Вартість повинна бути числом.\nСпробуйте ще раз."

    if price <= 0:
        return "Вартість повинна бути додатнім числом.\nСпробуйте ще раз."


def validate_date(date: str):

    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", date):
        return "Дата повинна бути у форматі YYYY-MM-DD. \nПриклад: 1900-01-01."

    date = datetime.strptime(date, "%Y-%m-%d").date()
    if date < datetime.now().date():
        return "Дата повинна бути більшою або дорівнювати поточній даті. \nСпробуйте ще раз."
