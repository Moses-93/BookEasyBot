from .admin import admin_keyboard
from .user import user_keyboard


class IdentifyRole:

    @staticmethod
    def generate_keyboard(user_role: str):
        if user_role == "master":
            return admin_keyboard.admin_main_menu()
        elif user_role == "user":
            return user_keyboard.main_keyboard()
