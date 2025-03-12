class BusinessInfoError(Exception):
    pass


class BusinessInfoHTTPError(BusinessInfoError):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Business-info error HTTP error: {status}: {message}")
