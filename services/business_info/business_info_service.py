import logging
from typing import Dict
from aiohttp import ClientResponseError
from core.exceptions.business_info_exception import BusinessInfoHTTPError
from ..api_client import APIClient


logger = logging.getLogger(__name__)


class BusinessInfoService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def create_business_info(self, user_id: int, business_info_data: Dict):
        logger.info("Launch the method to create the business information")
        try:
            created_business_info = await self.api_client.post(
                "/business-info", user_id, business_info_data
            )
            logger.info(f"created_business_info: {created_business_info}")
        except ClientResponseError as e:
            logger.error(f"Error when creating business information:  {e}")
            raise BusinessInfoHTTPError(e.status, e.message)
        return created_business_info

    async def update_business_info(self, user_id: int, business_info_data: Dict):
        try:
            updated_data = await self.api_client.patch(
                "/business-info", user_id, business_info_data
            )
        except ClientResponseError as e:
            raise BusinessInfoHTTPError(e.status, e.message)
        return updated_data

    async def delete_business_info(self, user_id: int):
        try:
            await self.api_client.delete("/business-info", user_id)
        except ClientResponseError as e:
            raise BusinessInfoHTTPError(e.status, e.message)
