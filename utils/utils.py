from datetime import date, time, datetime, timedelta
from typing import Dict


def calculate_reminder_time(data: Dict[str, date | time], offset: int = 2):
    date, time = data.get("date"), data.get("time")
    date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
    return date_time - timedelta(hours=offset)
