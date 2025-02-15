from aiogram import Router, F
from aiogram.types import Message

from services.api_client import api_client
from keyboards.admin import admin_keyboard
from keyboards.general import dynamic_keyboard

# from utils.formatted_view import format_referrals


router = Router()


MESSAGE = {
    "settings": "Ви перейшли в розділ налаштувань!\nТут ви можете керувати посиланнями, запрошенням, підпискою та багато іншого!",
    "Invitations_and_links": "Ви перейшли в розділ керування посиланнями та запрошеннями.\nТут ви можете запросити свого колегу, надати клієнтам посилання для запису та переглянути запрошених раніше майстрів!",
    "subscriptions": "Ви перейшли в розділ керування підпискою!Тут ви можете переглянути доступні плани, поточну підписку, оновити її або скасувати",
    "loyalty_program": "Ви перейшли в розділ для налаштування знижок клієнтам",
    "invite_master": "За цим посиланням зможуть зареєструватись інші майстри, після чого вам та новому майстру будуть нараховані бонуси у вигляді продовження підписки!\n\n*{link}*",
    "create_link_successfully": "Надайте це посилання вашим клієнтам:\n\n`{link}`\n\nЗа ним вони зможуть здійснити запис саме до вас!",
    "error_create_link": "❌ Не вдалося згенерувати посилання. Спробуйте пізніше.",
}


@router.message(F.text == "⚙️ Налаштування")
async def show_settings(message: Message):

    await message.answer(
        text=MESSAGE["settings"],
        reply_markup=admin_keyboard.manage_settings(),
    )


@router.message(F.text == "📲 Посилання для клієнтів")
async def generate_link(message: Message):

    status, user = await api_client.get(
        endpoint="/users/", chat_id=message.from_user.id
    )

    if status != 200 or not user:
        await message.answer(MESSAGE["error_create_link"])
        return
    master_id = user["id"]
    link = f"https://t.me/book_easy_bot?start=sign-up-master_{master_id}"

    await message.answer(
        text=MESSAGE["create_link_successfully"].format(link=link),
        parse_mode="Markdown",
    )


@router.message(F.text == "📤 Запрошення та посилання")
async def Invitations_and_links(message: Message):
    await message.answer(
        text=MESSAGE["Invitations_and_links"],
        reply_markup=admin_keyboard.manage_referrals(),
    )


@router.message(F.text == "💳 Підписка")
async def subscriptions(message: Message):
    await message.answer(
        text=MESSAGE["subscriptions"],
        reply_markup=admin_keyboard.manage_subscriptions(),
    )


@router.message(F.text == "🎁 Програма лояльності")
async def loyalty_program(message: Message):
    await message.answer(
        text=MESSAGE["loyalty_program"],
        reply_markup=admin_keyboard.manage_loyalty_program(),
    )


@router.message(F.text == "🤝 Запросити колегу")
async def invite_master(message: Message):
    status, master_id = await api_client.get(
        endpoint="/users/", chat_id=message.from_user.id
    )

    if status != 200 or not master_id:
        await message.answer(MESSAGE["error_create_link"])
        return

    link = f"https://t.me/book_easy_bot?start=ref_master_{master_id}"
    await message.answer(
        text=MESSAGE["invite_master"],
    )


@router.message(F.text == "👥 Запрошені майстри")
async def show_referrals(message: Message):
    status, referrals = await api_client.get(
        endpoint="/users/referrals/", chat_id=message.from_user.id
    )
    if status != 200:
        await message.answer(text=MESSAGE["error"])
        return
    # await message.answer(
    #     text=format_referrals(referrals)
    # )
