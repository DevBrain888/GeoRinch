"""Обработчик команды /start"""
import logging
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import get_main_keyboard
from handlers.notifications import add_user_to_main_menu

logger = logging.getLogger(__name__)


async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
        welcome_text = """Добро пожаловать в бота Карта ФЭК РГЭУ (РИНХ 🗺)!

😎Здесь вы сможете найти нужный вам кабинет и ориентироваться по колледжу

Для начала работы выберите нужный режим на клавиатуре ниже: 

- Поиск кабинета❓
- Карта колледжа🗺
- Как пройти от моего кабинета до другого
- Справочник✏️
- Избранное⭐️

Внимание! Бот находиться на стадий тестирования, поэтому могут быть небольшие ошибки или неточности."""
        await message.answer(welcome_text)
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
        # Отслеживаем, что пользователь в главном меню
        user_id = message.from_user.id if message.from_user else None
        if user_id:
            add_user_to_main_menu(user_id)
    except Exception as e:
        logger.error(f"Ошибка в обработчике cmd_start: {e}", exc_info=True)
        # Не отправляем ошибку пользователю, только логируем


def register_start_handler(dp: Dispatcher):
    """Регистрирует обработчик команды /start"""
    dp.message.register(cmd_start, CommandStart())

