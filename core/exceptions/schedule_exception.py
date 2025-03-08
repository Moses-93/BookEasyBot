class ScheduleServiceError(Exception):
    """Базовий клас винятків для сервісу розкладу"""

    pass


class ScheduleServiceHTTPError(ScheduleServiceError):
    """Помилка HTTP-запиту до сервісу розкладу"""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")
