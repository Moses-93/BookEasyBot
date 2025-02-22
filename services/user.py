from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiohttp import ClientResponseError
from services.api_client import APIClient
from states.auth import AuthState
from keyboards.factory_method import IdentifyRole
from keyboards.general import request_contact
from core.constants import REGISTRATIONS_MESSAGE


class UserService:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    async def get_user(self, chat_id: int):
        try:
            status, user = await self.api_client.get(
                endpoint="/users/", chat_id=chat_id
            )
            return user
        except ClientResponseError as e:
            if e.status == 401:
                return None
            raise

    async def add_new_master(self, user_id, master_chat_id: int):
        status, user = await self.api_client.post(
            "/users/masters/",
            user_id,
            json={"master_chat_id":master_chat_id}
            )
        return status, user

    async def create_user(self, user_data: dict):
        status, user = await self.api_client.post("/users/", user_data["chat_id"], json=user_data)
        return user


class RegistrationHandler:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def start_registration(
        self,
        message: Message,
        state: FSMContext,
        user_id: int,
        master_chat_id: int = None,
        role: str = "client",
    ):
        await state.update_data(
            name=message.from_user.full_name,
            username=message.from_user.username,
            role=role,
            master_chat_id=master_chat_id,
            chat_id=user_id,
        )

        await message.answer(
            text=REGISTRATIONS_MESSAGE["sign_up"],
            reply_markup=request_contact.request_phone(),
        )
        await state.set_state(AuthState.phone_number)

    async def complete_registration(self, message: Message, state: FSMContext):
        phone_number = message.contact.phone_number
        await state.update_data(phone_number=phone_number)
        user_data = await state.get_data()

        user = await self.user_service.create_user(user_data)
        if user:
            await message.answer(
                text=REGISTRATIONS_MESSAGE[
                    f"successful_register_{user['role']}"
                ].format(name=user["name"]),
                reply_markup=IdentifyRole.generate_keyboard(user["role"]),
            )
