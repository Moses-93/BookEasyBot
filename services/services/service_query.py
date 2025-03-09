from aiohttp import ClientResponseError
from typing import Dict, List, Optional, Union

from core.exceptions.service_exception import ServiceHTTPError
from ..api_client import APIClient


class ServiceQuery:

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def create_service(self, user_id: int, data: Dict) -> Optional[Dict]:
        try:
            created_service = await self.api_client.post("/services", user_id, data)
        except ClientResponseError as e:
            raise ServiceHTTPError(e.status, e.message)
        return created_service

    async def deactivate_service(self, user_id: int, service_id: int):
        try:
            await self.api_client.patch(f"/services/deactivate/{service_id}", user_id)
        except ClientResponseError as e:
            raise ServiceHTTPError(e.status, e.message)

    async def get_services(
        self, user_id: int
    ) -> Optional[List[Dict[str, Union[int, str]]]]:
        try:
            services = await self.api_client.get("/services", user_id)
        except ClientResponseError as e:
            raise ServiceHTTPError(e.status, e.message)
        return services

    async def update_service(
        self, user_id: int, service_id: int, data: Dict[str, str]
    ) -> None:
        try:
            endpoint = f"/services/{service_id}"
            await self.api_client.patch(endpoint, user_id, data)
        except ClientResponseError as e:
            raise ServiceHTTPError(e.status, e.message)
