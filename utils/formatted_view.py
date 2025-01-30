import logging
from typing import List, Dict


logger = logging.getLogger(__name__)


def sorted_data(data: List[Dict]):
    return sorted(data, key=lambda x: x["id"])


def format_service(data: List[Dict]):
    """Форматування послуг для відображення користувачу."""

    formatted = f"📋 *ДОСТУПНІ ПОСЛУГИ*\n\n"
    for item in sorted_data(data):
        formatted += f"🖌️ *{item.get("name")} - {item.get("price")} грн.*\n\n"
    return formatted


def format_date(data: List[Dict]):
    """Форматування дат для відображення користувачу."""

    formatted = f"📅 *ДОСТУПНІ ДАТИ*\n\n"
    for item in sorted_data(data):
        formatted += f"*{item.get("date")}*\n" f"{'-' * 30}\n"

    return formatted


def format_time(data: List[Dict]):
    """Форматування дат для відображення користувачу."""

    formatted = f"⏰ *ДОСТУПНІ ГОДИНИ*\n\n"
    for item in sorted_data(data):
        formatted += f"*{item.get("time")}*\n" f"{'-' * 30}\n"
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
    for booking in bookings:
        formatted += (
            f"👤 *{booking.get("name")}*\n"
            f"🆔 *{booking.get("service")}*\n"
            f"📅 *{booking.get("date")}*\n"
            f"⏰ *{booking.get("time")}*\n"
            f"{'-' * 30}\n"
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
