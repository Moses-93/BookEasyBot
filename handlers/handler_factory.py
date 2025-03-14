from services import (
    api_client,
    schedules,
    services,
    user as user_service,
    business_info,
    subscriptions,
    invites,
)
from keyboards import admin, general, user
from handlers.admin import (
    DateCommandHandler,
    DateRouter,
    TimeCommandHandler,
    TimeRouter,
    ServiceCommandHandler,
    ServiceRouter,
    BusinessInfoCommandHandler,
    BusinessInfoRouter,
    SubscriptionCommandHandler,
    SubscriptionRouter,
    InviteCommandHandler,
    InviteRouter,
)


class HandlerFactory:

    def __init__(self, base_url: str, api_token: str):
        self.api_client = api_client.APIClient(base_url, api_token)
        self.date_service = schedules.DateService(self.api_client)
        self.display_data_keyboard = general.DisplayDataKeyboard()
        self.user_service = user_service.UserService(self.api_client)
        self.admin_keyboard = admin.AdminKeyboard()

    def create_date_router(self) -> DateRouter:
        date_manager = schedules.DateManager(
            self.date_service,
            self.user_service,
            self.admin_keyboard,
            self.display_data_keyboard,
        )
        date_command_handler = DateCommandHandler(date_manager)
        return DateRouter(date_command_handler)

    def create_time_router(self) -> TimeRouter:
        time_service = schedules.TimeService(self.api_client)
        time_manager = schedules.TimeManager(time_service, self.date_service)
        time_command_handler = TimeCommandHandler(time_manager)
        return TimeRouter(time_command_handler)

    def create_service_router(self) -> ServiceRouter:
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
        service_command_handler = ServiceCommandHandler(service_manager)
        return ServiceRouter(service_command_handler)

    def create_business_info_router(self) -> BusinessInfoRouter:
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
        business_info_command_handler = BusinessInfoCommandHandler(
            business_info_manager
        )
        return BusinessInfoRouter(business_info_command_handler)

    def create_subscription_router(self):
        subscription_service = subscriptions.SubscriptionService(self.api_client)
        subscription_manager = subscriptions.SubscriptionManager(
            subscription_service, self.user_service, self.admin_keyboard
        )
        subscription_command_handler = SubscriptionCommandHandler(subscription_manager)
        return SubscriptionRouter(subscription_command_handler)

    def create_invite_router(self):
        invite_service = invites.InviteService(self.api_client)
        invite_manager = invites.InviteManager(
            invite_service, self.user_service, self.admin_keyboard
        )
        invite_command_handler = InviteCommandHandler(invite_manager)
        return InviteRouter(invite_command_handler)
