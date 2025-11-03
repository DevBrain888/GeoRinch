"""Обработчики для функционала справочника"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import Message

from keyboards import get_main_keyboard, get_place_guide
from handlers.constants import GUIDE_ENTRY_TEXT, GUIDE_SHOP_TEXT, GUIDE_APTEKA_TEXT, GUIDE_SHOP, GUIDE_APTEKA
from handlers.notifications import add_user_to_main_menu, remove_user_from_main_menu

logger = logging.getLogger(__name__)


async def on_guide_entry(message: Message):
    """Старт сценария Справочник."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if user_id:
            remove_user_from_main_menu(user_id)  # Удаляем из главного меню при входе в справочник
        await message.answer("Выберите пункт:", reply_markup=get_place_guide())
    except Exception as e:
        logger.error(f"Ошибка в on_guide_entry: {e}", exc_info=True)


async def on_guide_select(message: Message):
    """Обработка выбора пункта справочника и возврат в меню."""
    try:
        text = (message.text or "").strip()
        # По вашему указанию: для "Магазин пятерочка" отправляем URL из строки 36 (GUIDE_APTEKA)
        if text == GUIDE_SHOP_TEXT:
            await message.answer_photo(photo=GUIDE_APTEKA)
        elif text == GUIDE_APTEKA_TEXT:
            await message.answer_photo(photo=GUIDE_SHOP)
        else:
            return
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
        # Отслеживаем, что пользователь вернулся в главное меню
        user_id = message.from_user.id if message.from_user else None
        if user_id:
            add_user_to_main_menu(user_id)
    except Exception as e:
        logger.error(f"Ошибка в on_guide_select: {e}", exc_info=True)


def register_guide_handlers(dp: Dispatcher):
    """Регистрация обработчиков справочника."""
    dp.message.register(on_guide_entry, F.text == GUIDE_ENTRY_TEXT)
    dp.message.register(
        on_guide_select,
        F.text.in_({GUIDE_SHOP_TEXT, GUIDE_APTEKA_TEXT}),
    )

