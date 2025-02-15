from aiogram import Router, F
from aiogram.types import Message

from services.api_client import api_client
from keyboards.admin import admin_keyboard


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
async def show_setting(message: Message):

    await message.answer(
        text=MESSAGE["settings"],
        reply_markup=admin_keyboard.manage_settings(),
    )


@router.message(F.text == "🔗 Посилання клієнтам")
async def generate_link(message: Message):

    status, master_id = await api_client.get(
        endpoint="/users/", chat_id=message.from_user.id
    )

    if status != 200 or not master_id:
        await message.answer(MESSAGE["error_create_link"])
        return

    link = f"https://t.me/book_easy_bot?start=master_{master_id}"
    await message.answer(
        text=MESSAGE["create_link_successfully"].format(link=link),
        parse_mode="Markdown",
    )
