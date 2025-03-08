from core.dependencies import settings
from .time_service import TimeManager, TimeService
from .date_service import DateManager, DateService
from ..api_client import APIClient


class ScheduleFactory:
    def __init__(self):
        self.http_client = APIClient("http://0.0.0.0:8000/api/v1", settings.api_token)
        self.date_service = DateService(self.http_client)
        self.time_service = TimeService(self.http_client)

    def create_date_manager(self) -> DateManager:
        return DateManager(self.date_service)

    def create_time_service(self) -> TimeManager:
        return TimeManager(self.time_service, self.date_service)
