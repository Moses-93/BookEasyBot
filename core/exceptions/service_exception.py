class ServiceError(Exception):
    pass


class ServiceHTTPError(ServiceError):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Service HTTP error: {status}: {message}")
