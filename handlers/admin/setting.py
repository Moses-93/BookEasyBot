from aiogram import Router, F
from aiogram.types import Message

from services.api_client import api_client
from keyboards.admin import admin_keyboard


router = Router()


MESSAGE = {
    "start": "Ви перейшли в розділ налаштувань!\nТут ви можете згенерувати посилання для ваших клієнтів, керувати підпискою та багато іншого!",
    "create_link_successfully": "Надайте це посилання вашим клієнтам.\nЗа ним вони зможуть здійснити запис саме до вас!\n\n*{link}*",
    "error_create_link": "❌ Не вдалося згенерувати посилання. Спробуйте пізніше.",
}


@router.message(F.text == "⚙️ Налаштування")
async def show_setting(message: Message):

    await message.answer(
        text=MESSAGE["start"],
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
