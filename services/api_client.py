import logging
from typing import List, Dict
from aiohttp import ClientSession, ClientResponseError
from core.dependencies import settings

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_token}"}

    async def _make_request(self, method: str, endpoint: str, chat_id: int, **kwargs):
        """
        Основний метод для виконання HTTP-запитів.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {**self.headers, "X-Chat-ID": str(chat_id)}

        async with ClientSession() as session:
            async with session.request(
                method, url, headers=headers, **kwargs
            ) as response:
                status = response.status
                data = await response.json()
                text = await response.text()
                if status >= 400:
                    logger.warning(f"status: {status}. message: {text}")
                    raise ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                    )

                return status, data

    async def get(
        self, endpoint: str, chat_id: int, params: dict = None
    ) -> List[Dict] | str:
        """
        Виконання GET-запиту.
        """
        return await self._make_request("GET", endpoint, chat_id, params=params)

    async def post(self, endpoint: str, chat_id: int, json: dict = None):
        """
        Виконання POST-запиту.
        """
        return await self._make_request("POST", endpoint, chat_id, json=json)

    async def put(self, endpoint: str, chat_id: int, json: dict = None):
        """
        Виконання PUT-запиту.
        """
        return await self._make_request("PUT", endpoint, chat_id, json=json)

    async def patch(self, endpoint: str, chat_id: int, json: dict = None):
        """
        Виконання PATCH-запиту.
        """
        return await self._make_request("PATCH", endpoint, chat_id, json=json)

    async def delete(self, endpoint: str, chat_id: int):
        """
        Виконання DELETE-запиту.
        """
        return await self._make_request("DELETE", endpoint, chat_id)


api_client = APIClient(
    base_url="http://0.0.0.0:8000/api/v1", api_token=settings.api_token
)
