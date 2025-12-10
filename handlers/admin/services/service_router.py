from aiogram import Router, F
from states.service import (
    CreateServiceState,
    UpdateServiceState,
    DeleteServiceState,
)
from .service_handlers import ServiceCommandHandler


class ServiceRouter:
    def __init__(self, service_command_handler: ServiceCommandHandler):
        self.router = Router()
        self._register_handlers(service_command_handler)

    def _register_handlers(self, handler: ServiceCommandHandler):
        """Реєстрація всіх обробників."""
        self.router.message.register(handler.start, F.text == "📖 Послуги")
        self.router.message.register(
            handler.start_create_service, F.text == "➕ Додати послугу"
        )
        self.router.message.register(
            handler.start_delete_service, F.text == "❌ Видалити послугу"
        )
        self.router.message.register(
            handler.start_edit_service, F.text == "🔄 Оновити послугу"
        )

        self.router.message.register(handler.set_service_name, CreateServiceState.name)
        self.router.message.register(
            handler.finish_create_service, CreateServiceState.price
        )
        self.router.callback_query.register(
            handler.finish_deactivate_service, DeleteServiceState.service
        )
        self.router.callback_query.register(
            handler.select_field_to_update, UpdateServiceState.name
        )
        self.router.callback_query.register(handler.set_field, UpdateServiceState.field)
        self.router.message.register(
            handler.finish_update_service, UpdateServiceState.new_value
        )
