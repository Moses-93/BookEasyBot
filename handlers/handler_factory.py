from services import (
    api_client,
    schedules,
    services,
    user as user_service,
    business_info,
)
from keyboards import admin, general, user
from .admin.schedules import schedule_routers, date, time
from .admin.services import service_handlers, service_router
from .admin.business_info import business_info_handlers, business_info_router


class HandlerFactory:

    def __init__(self, base_url: str, api_token: str):
        self.api_client = api_client.APIClient(base_url, api_token)
        self.date_service = schedules.DateService(self.api_client)
        self.display_data_keyboard = general.DisplayDataKeyboard()
        self.user_service = user_service.UserService(self.api_client)
        self.admin_keyboard = admin.AdminKeyboard()

    def create_date_router(self) -> schedule_routers.DateRouter:
        date_manager = schedules.DateManager(
            self.date_service,
            self.user_service,
            self.admin_keyboard,
            self.display_data_keyboard,
        )
        date_command_handler = date.DateCommandHandler(date_manager)
        return schedule_routers.DateRouter(date_command_handler)

    def create_time_router(self) -> schedule_routers.TimeRouter:
        time_service = schedules.TimeService(self.api_client)
        time_manager = schedules.TimeManager(time_service, self.date_service)
        time_command_handler = time.TimeCommandHandler(time_manager)
        return schedule_routers.TimeRouter(time_command_handler)

    def create_service_router(self) -> service_router.ServiceRouter:
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

    def create_business_info_router(self) -> business_info_router.BusinessInfoRouter:
        business_info_service = business_info.BusinessInfoService(self.api_client)
        create_manager = business_info.BusinessInfoCreateManager(business_info_service)
        update_manager = business_info.BusinessInfoUpdateManager(business_info_service)
        business_info_manager = business_info.BusinessInfoManager(
            create_manager,
            update_manager,
            business_info_service,
            self.user_service,
            self.admin_keyboard,
        )
        business_info_command_handler = (
            business_info_handlers.BusinessInfoCommandHandler(business_info_manager)
        )
        return business_info_router.BusinessInfoRouter(business_info_command_handler)
