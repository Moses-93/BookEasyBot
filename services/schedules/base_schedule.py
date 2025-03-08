from typing import Any, Dict, List, Optional
from aiohttp import ClientResponseError
from ..api_client import APIClient
from core.exceptions.schedule_exception import ScheduleServiceHTTPError


class BaseScheduleService:

    def __init__(self, http_client: APIClient):
        self.http_client = http_client

    async def get(self, endpoint: str, user_id: int) -> Optional[List[Dict[str, Any]]]:
        try:
            data = await self.http_client.get(endpoint, user_id)
        except ClientResponseError as e:
            raise ScheduleServiceHTTPError(e.status, e.message)
        return data

    async def create(self, endpoint: str, user_id: int, data: Dict[str, Any]):
        try:
            response = await self.http_client.post(endpoint, user_id, data)
        except ClientResponseError as e:
            raise ScheduleServiceHTTPError(e.status, e.message)
        return response

    async def deactivate(self, endpoint: str, user_id: int):
        try:
            response = await self.http_client.patch(endpoint, user_id)
        except ClientResponseError as e:
            raise ScheduleServiceHTTPError(e.status, e.message)
        return response
