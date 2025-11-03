"""Обработчики для функционала карты колледжа"""
import logging
from typing import Dict, Any
from aiogram import Dispatcher, F
from aiogram.types import Message

from keyboards import get_main_keyboard, get_floor_selection_keyboard
from handlers.constants import MAP_ENTRY_TEXT, FLOOR_1_TEXT, FLOOR_2_TEXT, FLOOR_3_TEXT, FLOOR_4_TEXT
from handlers.utils import parse_floor_label, get_floor_image_url

logger = logging.getLogger(__name__)

# Простая FSM для сценария "Карта колледжа"
_map_state: Dict[int, Dict[str, Any]] = {}


def is_user_in_map_mode(user_id: int) -> bool:
    """Проверка, находится ли пользователь в режиме карты."""
    st = _map_state.get(user_id)
    return st is not None and st.get("step") == "await_floor"


def _is_map_waiting_floor(message: Message) -> bool:
    """Проверка, ожидает ли бот выбора этажа для карты."""
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    st = _map_state.get(user_id)
    if not st:
        return False
    return st.get("step") == "await_floor"


async def on_map_entry(message: Message):
    """Старт сценария Карта колледжа."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        _map_state[user_id] = {"step": "await_floor"}
        await message.answer("Выберите этаж:", reply_markup=get_floor_selection_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в on_map_entry: {e}", exc_info=True)


async def on_map_floor(message: Message):
    """Обработка выбора этажа для карты."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        st = _map_state.get(user_id)
        if not st:
            return
        floor = parse_floor_label(message.text)
        if floor is None:
            return
        image_url = get_floor_image_url(floor)
        if image_url:
            await message.answer_photo(photo=image_url)
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
        _map_state.pop(user_id, None)
    except Exception as e:
        logger.error(f"Ошибка в on_map_floor: {e}", exc_info=True)


def register_map_handlers(dp: Dispatcher):
    """Регистрация обработчиков карты колледжа."""
    dp.message.register(on_map_entry, F.text == MAP_ENTRY_TEXT)
    dp.message.register(
        on_map_floor,
        F.text.in_({FLOOR_1_TEXT, FLOOR_2_TEXT, FLOOR_3_TEXT, FLOOR_4_TEXT}),
        _is_map_waiting_floor,
    )

