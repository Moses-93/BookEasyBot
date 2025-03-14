from aiogram import Router, F

from handlers.admin.invites import InviteCommandHandler


class InviteRouter:
    def __init__(self, invite_command_handlers: InviteCommandHandler):
        self.router = Router()
        self._register_handlers(invite_command_handlers)

    def _register_handlers(self, handler: InviteCommandHandler):
        """Реєстрація обробників."""
        self.router.message.register(
            handler.start, F.text == "📤 Запрошення та посилання"
        )
        self.router.message.register(
            handler.invite_to_client, F.text == "📲 Посилання для клієнтів"
        )
        self.router.message.register(handler.back_button, F.text == "🔙 Назад")
