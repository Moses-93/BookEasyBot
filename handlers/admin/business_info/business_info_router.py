from aiogram import Router, F

from states.business_info import CreateBusinessInfoState, UpdateBusinessInfoState
from .business_info_handlers import BusinessInfoCommandHandler


class BusinessInfoRouter:
    def __init__(self, business_info_command_handler: BusinessInfoCommandHandler):
        self.router = Router()
        self._register_handlers(business_info_command_handler)

    def _register_handlers(self, handler: BusinessInfoCommandHandler):
        """Реєстрація обробників."""
        self.router.message.register(handler.start, F.text == "📔 Контакти")
        self.router.message.register(handler.start_add_info, F.text == "➕ Додати дані")
        self.router.message.register(
            handler.start_edit_info, F.text == "🔄 Оновити дані"
        )
        self.router.message.register(handler.set_name, CreateBusinessInfoState.name)
        self.router.message.register(
            handler.set_address, CreateBusinessInfoState.address
        )
        self.router.message.register(
            handler.set_phone_number, CreateBusinessInfoState.phone_number
        )
        self.router.message.register(
            handler.set_description, CreateBusinessInfoState.description
        )
        self.router.message.register(
            handler.set_google_link, CreateBusinessInfoState.google_link
        )
        self.router.message.register(
            handler.set_telegram_link, CreateBusinessInfoState.telegram_link
        )
        self.router.message.register(
            handler.set_instagram_link, CreateBusinessInfoState.instagram_link
        )
        self.router.callback_query.register(
            handler.handle_skip, F.data.startswith("skip_")
        )
        self.router.callback_query.register(
            handler.confirm_create_business_info,
            F.data == "confirm_create_business_info",
        )
        self.router.callback_query.register(
            handler.start_update_field, UpdateBusinessInfoState.field
        )
        self.router.message.register(
            handler.update_field_value, UpdateBusinessInfoState.new_value
        )
