import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from services.user import RegistrationHandler, UserService
from services.api_client import api_client
from states.auth import AuthState
from keyboards.factory_method import IdentifyRole
from keyboards.general import dynamic_keyboard
from keyboards.user import user_keyboard
from utils.filters import DeepLinkFilter
from core.constants import REGISTRATIONS_MESSAGE


router = Router()
logger = logging.getLogger(__name__)
user_service = UserService(api_client)
registration_handler = RegistrationHandler(user_service)


class CommandHandler:
    def __init__(
        self,
        user_service: UserService,
        registration_handler: RegistrationHandler,
        router: Router,
    ):
        self.user_service = user_service
        self.registration_handler = registration_handler
        self.router = router
        self._register_handlers()

    def _register_handlers(self):
        """Реєстрація обробників."""
        self.router.message.register(
            self.start_sign_up,
            CommandStart(deep_link=True),
            DeepLinkFilter(prefix="master"),
        )
        self.router.message.register(self.start, CommandStart())
        self.router.message.register(self.become_master, F.text == "✅ Стати майстром")
        self.router.message.register(
            self.registration_handler.complete_registration, AuthState.phone_number
        )

    async def _is_user_linked_to_master(self, user: dict, master_chat_id: int) -> bool:
        logger.info(f"Перевірка майстрів користувача")
        return master_chat_id in [
            master["chat_id"] for master in user.get("masters", [])
        ]

    async def start_sign_up(self, message: Message, state: FSMContext, user_id: int):
        """Обробка команди /start з deeplink."""
        logger.info(f"Реєстрація користувача за посиланням майстра")
        master_chat_id = message.text.split("-")[1]
        try:
            master_chat_id = int(master_chat_id)
        except ValueError:
            return await message.answer("Посилання має некоректний формат!")
        user = await self.user_service.get_user(user_id)
        logger.info(f"User: {user}")

        if not user:
            logger.info(
                f"Користувач {user_id} не зераєстрований. Початок процесу реєстрації"
            )

            return await self.registration_handler.start_registration(
                message, state, user_id, master_chat_id
            )
        elif await self._is_user_linked_to_master(user, master_chat_id):
            logger.info(f"Користувач вже має цього майстра")

            return await message.answer(
                text=REGISTRATIONS_MESSAGE["client"],
                reply_markup=user_keyboard.main_keyboard(),
            )
        else:
            logger.info(f"Користувач не має цього майстра. Додаємо")
            status, user = await self.user_service.add_new_master(
                user_id, master_chat_id
            )
            if status == 204:
                logger.info("Додали нового майстра")
                return await message.answer(
                    text=REGISTRATIONS_MESSAGE["client"],
                    reply_markup=user_keyboard.main_keyboard(),
                )

    async def start(self, message: Message, user_id: int):
        """Обробка команди /start."""
        user = await self.user_service.get_user(user_id)
        if not user:
            await message.answer(
                text=REGISTRATIONS_MESSAGE["info"],
                reply_markup=dynamic_keyboard.dynamic_reply_keyboard(
                    ["✅ Стати майстром"]
                ),
            )
            return
        await message.answer(
            text=REGISTRATIONS_MESSAGE[user["role"]].format(name=user["name"]),
            reply_markup=IdentifyRole.generate_keyboard(user["role"]),
        )

    async def become_master(self, message: Message, state: FSMContext, user_id: int):
        """Обробка кнопки 'Стати майстром'."""
        await self.registration_handler.start_registration(
            message, state, user_id, role="master"
        )


command_handler = CommandHandler(user_service, registration_handler, router)
