from services import api_client, schedules, services, user as user_service
from keyboards import admin, general, user
from .admin.schedules import date, time
from .admin.services import service_handlers, service_router


class HandlerFactory:

    def __init__(self, base_url: str, api_token: str):
        self.api_client = api_client.APIClient(base_url, api_token)
        self.date_service = schedules.DateService(self.api_client)
        self.display_data_keyboard = general.DisplayDataKeyboard()
        self.user_service = user_service.UserService(self.api_client)
        self.admin_keyboard = admin.AdminKeyboard()

    def create_date_admin_handler(self) -> date.DateCommandHandler:
        date_manager = schedules.DateManager(self.date_service)
        return date.DateCommandHandler(date_manager)

    def create_time_admin_handler(self) -> time.TimeCommandHandler:
        time_service = schedules.TimeService(self.api_client)
        time_manager = schedules.TimeManager(time_service, self.date_service)
        return time.TimeCommandHandler(time_manager)

    def service_router(self) -> service_router.ServiceRouter:
        service_query = services.ServiceQuery(self.api_client)
        service_create_manager = services.ServiceCreateManager(service_query)
        service_edit_manager = services.ServiceEditManager(
            service_query, self.display_data_keyboard
        )
        service_deactivate_manager = services.ServiceDeactivateManager(
            service_query, self.display_data_keyboard
        )
        service_manager = services.ServiceManager(
            self.user_service,
            self.admin_keyboard,
            service_create_manager,
            service_deactivate_manager,
            service_edit_manager,
        )
        service_command_handler = service_handlers.ServiceCommandHandler(
            service_manager
        )
        return service_router.ServiceRouter(service_command_handler)
