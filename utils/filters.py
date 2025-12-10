from aiogram.filters import BaseFilter
from aiogram.types import Message


class DeepLinkFilter(BaseFilter):
    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, message: Message) -> bool:
        if not message.text or not message.text.startswith("/start"):
            return False

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return False

        deep_link_param = parts[1]
        return deep_link_param.startswith(self.prefix)
