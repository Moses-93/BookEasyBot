from collections import defaultdict
import logging
from typing import List, Dict, Union


logger = logging.getLogger(__name__)


def sorted_data(data: List[Dict]):
    return sorted(data, key=lambda x: x["id"])


def format_service(data: List[Dict]):
    """Форматування послуг для відображення користувачу."""

    formatted = f"📋 *ДОСТУПНІ ПОСЛУГИ*\n\n"
    for item in sorted_data(data):
        formatted += (
            f"*{item.get("name")} - {item.get("price")} грн.*\n" f"{'-' * 30}\n"
        )

    return formatted


def format_date(data: List[Dict]):
    """Форматування дат для відображення користувачу."""

    formatted = f"📅 *ДОСТУПНІ ДАТИ*\n\n"
    for item in sorted_data(data):
        formatted += f"*{item.get("date")}*\n" f"{'-' * 30}\n"

    return formatted


def format_time(times: List[Dict]) -> str:

    grouped_data = defaultdict(list)
    for item in sorted(times, key=lambda x: x["date"]["date"]):
        date = item["date"]["date"]
        time = item["time"][:5]
        grouped_data[date].append(time)

    formatted = "⏰ *ДОСТУПНІ ГОДИНИ*\n\n"
    for date, times in grouped_data.items():
        formatted += f"📅 *{date}*\n"
        formatted += "\n".join(f"⏱ {time}" for time in times) + "\n"
        formatted += "➖" * 10 + "\n"

    return formatted


def format_reviews(reviews):
    """Форматування відгуків для виводу."""

    formatted = "📝 *Відгуки клієнтів*\n\n"
    for review in reviews:
        stars = "⭐" * review["rating"] + "✩" * (5 - review["rating"])
        formatted += (
            f"👤 *{review['name']}*\n"
            f"⭐ Рейтинг: {stars} ({review['rating']}/5)\n"
            f"💬 {review['comment']}\n"
            f"{'-' * 30}\n"
        )
    return formatted


def format_admin(data: List[Dict]):
    """Форматування користувачів для відображення."""

    formatted = f"⏰ *АДМІНІСТРАТОРИ*\n\n"
    for item in sorted_data(data):
        formatted += (
            f"👤 *{item.get("name")}*\n" f"🆔 *{item.get("chat_id")}*\n" f"{'-' * 30}\n"
        )
    return formatted


def format_booking(bookings: List[Dict]):
    """Форматування записів для виводу."""

    formatted = "📝 *ЗАПИСИ*\n\n"
    for num, booking in enumerate(bookings):
        formatted += (
            f"🆔 *{num + 1}*\n"
            f"👤 *{booking["user"].get("username")}*\n"
            f"📞 *{booking["user"].get("phone")}*\n"
            f"📌 *{booking["service"].get("name")}*\n"
            f"📅 *{booking["date"].get("date")}*\n"
            f"⏰ *{booking["time"].get("time")}*\n"
            f"{'-  ' * 20}\n"
        )
    return formatted


def format_business_info(business_info: List[Dict]):
    """Форматування записів для виводу."""

    formatted = "📝 *ДЕТАЛЬНА ІНФОРМАЦІЯ*\n\n"
    for info in business_info:
        formatted += (
            f"👤 *{info.get('name')}*\n"
            f"📍 Адреса: *{info.get('address')}*\n"
            f"📞 Телефон: *{info.get('phone')}*\n"
            f"ℹ️ Опис: *{info.get('description')}*\n"
            f"🕒 Графік роботи: *{info.get('working_hours')}*\n"
            f"🌍 Карта: [Посилання]({info.get('google_maps_url')})\n"
        )
    return formatted
