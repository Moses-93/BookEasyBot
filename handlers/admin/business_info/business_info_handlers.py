import logging
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from services.business_info.business_info_manager import BusinessInfoManager


logger = logging.getLogger(__name__)


class BusinessInfoCommandHandler:

    def __init__(self, business_info_manager: BusinessInfoManager):
        self.business_info_manager = business_info_manager

    async def start(self, message: Message, user_id: int):
        msg, keyboard = await self.business_info_manager.start(user_id)
        await message.answer(text=msg, reply_markup=keyboard)

    async def send_skip_message(self, message: Message, state: FSMContext, next_state):
        logger.info(f"Launch the handler to skip message. Next state: {next_state}")
        msg, keyboard = (
            await self.business_info_manager.creation_manager.send_skip_message(
                state, next_state
            )
        )
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def start_add_info(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to start create business info")
        msg = await self.business_info_manager.creation_manager.start_add_info(state)
        await message.answer(text=msg, parse_mode="Markdown")

    async def start_edit_info(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to start edit business info")
        msg, keyboard = await self.business_info_manager.update_manager.start_edit_info(
            state
        )
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def set_name(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set name")

        name = message.text
        msg = await self.business_info_manager.creation_manager.set_name(state, name)
        await message.answer(text=msg, parse_mode="Markdown")

    async def set_address(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set address")

        address = message.text
        msg = await self.business_info_manager.creation_manager.set_address(
            state, address
        )
        await message.answer(text=msg, parse_mode="Markdown")

    async def set_phone_number(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set phone_number")

        phone = message.text
        msg, keyboard = (
            await self.business_info_manager.creation_manager.set_phone_number(
                state, phone
            )
        )
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def set_description(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set description")

        description = message.text
        msg, keyboard = (
            await self.business_info_manager.creation_manager.set_description(
                state, description
            )
        )
        await message.answer(text=msg, reply_markup=keyboard)

    async def set_google_link(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set google link")

        google_maps_link = message.text
        msg, keyboard = (
            await self.business_info_manager.creation_manager.set_google_link(
                state, google_maps_link
            )
        )
        await message.answer(text=msg, reply_markup=keyboard)

    async def set_telegram_link(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set telegram link")

        telegram_link = message.text
        msg, keyboard = (
            await self.business_info_manager.creation_manager.set_telegram_link(
                state, telegram_link
            )
        )
        await message.answer(text=msg, reply_markup=keyboard)

    async def set_instagram_link(self, message: Message, state: FSMContext):
        logger.info("Launch the handler to set instagram link")

        instagram_link = message.text
        msg, keyboard = (
            await self.business_info_manager.creation_manager.set_instagram_link(
                state, instagram_link
            )
        )
        await message.answer(text=msg, reply_markup=keyboard, parse_mode="Markdown")

    async def handle_skip(self, callback: CallbackQuery, state: FSMContext):
        logger.info(f"Launch the handler to handle skip message.")

        num = callback.data.split("_")[1]
        msg, keyboard = await self.business_info_manager.creation_manager.handle_skip(
            state, num
        )
        await callback.message.answer(
            text=msg, reply_markup=keyboard, parse_mode="Markdown"
        )

    async def confirm_create_business_info(
        self, callback: CallbackQuery, state: FSMContext, user_id: int
    ):
        logger.info("Launch the handler to confirm creating business information")
        msg = await self.business_info_manager.creation_manager.finish_create_business_info(
            state, user_id
        )
        await callback.message.answer(text=msg, parse_mode="Markdown")

    async def start_update_field(self, callback: CallbackQuery, state: FSMContext):
        field = callback.data
        msg = await self.business_info_manager.update_manager.start_update_field(
            state, field
        )
        await callback.message.edit_text(text=msg, parse_mode="Markdown")

    async def update_field_value(
        self, message: Message, state: FSMContext, user_id: int
    ):
        new_value = message.text
        msg = await self.business_info_manager.update_manager.update_field_value(
            state, new_value, user_id
        )
        await message.answer(text=msg, parse_mode="Markdown")
