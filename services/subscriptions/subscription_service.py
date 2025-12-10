import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from aiohttp import ClientResponseError

from core.exceptions.subscription_exception import SubscriptionHTTPError
from ..api_client import APIClient


logger = logging.getLogger(__name__)


class SubscriptionService:

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def is_subscription_expiring(self, end_date: datetime) -> bool:
        return end_date <= datetime.now() + timedelta(days=5)

    def format_plan(self, plan: Dict[str, Any]) -> str:
        return (
            f"📌 *{plan['name']}*\n\n"
            f"*{plan['description']}*\n\n"
            f"💰 *Вартість: {plan['price']} грн*\n"
            f"⏳ *Тривалість: {plan['duration_days']} днів*\n"
        )

    def format_subscription(self, subscription: Dict) -> str:
        start_date = datetime.fromisoformat(subscription["start_date"]).strftime(
            "%d.%m.%Y %H:%M"
        )
        end_date = datetime.fromisoformat(subscription["end_date"]).strftime(
            "%d.%m.%Y %H:%M"
        )
        formatted = (
            f"🌟 *Твій план: {subscription['plan']['name']}*\n"
            f"💸 *Скільки коштує: {subscription['plan']['price']}* грн\n"
            f"🚀 *Ти з нами з: {start_date}*\n"
            f"⏳ *Ти з нами до: {end_date}*"
        )
        return formatted

    async def cancel_user_subscription(
        self, user_id: int
    ) -> Dict[str, Union[float, bool]]:
        try:
            return await self.api_client.get("/subscriptions/cancel-preview", user_id)
        except ClientResponseError as e:
            raise SubscriptionHTTPError(e.status, e.message)

    async def get_user_subscription(
        self, chat_id: int
    ) -> Dict[
        str, Union[int, datetime, Dict[str, Union[int, float, datetime, bool, str]]]
    ]:
        try:
            return await self.api_client.get("/subscriptions/", chat_id)
        except ClientResponseError as e:
            logger.error(f"ClientResponseError: {e}")
            raise SubscriptionHTTPError(e.status, e.message)

    async def get_subscription_plan(
        self, user_id: int
    ) -> Dict[str, Union[int, float, datetime, bool, str]]:
        try:
            return await self.api_client.get("/subscriptions/plans", user_id)
        except ClientResponseError as e:
            raise SubscriptionHTTPError(e.status, e.message)

    async def get_payment_url(self, plan_id: int, plan_price: int, chat_id: int) -> str:
        try:
            return await self.api_client.post(
                f"/payments/", chat_id, json={"id": plan_id, "price": plan_price}
            )
        except ClientResponseError as e:
            raise SubscriptionHTTPError(e.status, e.message)

    async def activate_free_subscription(self, user_id: int) -> Optional[bool]:
        try:
            await self.api_client.post("/activate-free", user_id)
        except ClientResponseError as e:
            if e.status == 409:
                return False
            raise SubscriptionHTTPError(e.status, e.message)
