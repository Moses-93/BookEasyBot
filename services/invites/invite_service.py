from services.api_client import APIClient


class InviteService:

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def create_link_to_client(self, user_chat_id: int) -> str:

        return f"https://t.me/book_easy_bot?start=master-{user_chat_id}"
