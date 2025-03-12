from ..api_client import APIClient


class SubscriptionService:

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
