"""Обработчики для функционала маршрута A→B"""
import logging
from typing import Dict, Any, Set
from aiogram import Dispatcher, F
from aiogram.types import Message

from keyboards import get_main_keyboard, get_floor_selection_keyboard
from handlers.constants import (
    ROUTE_ENTRY_TEXT,
    FLOOR_1_TEXT,
    FLOOR_2_TEXT,
    FLOOR_3_TEXT,
    FLOOR_4_TEXT,
    FIRST_FLOOR_ROOM_BUTTONS,
    SECOND_FLOOR_ROOM_BUTTONS,
    THIRD_FLOOR_ROOM_BUTTONS,
    FOURTH_FLOOR_ROOM_BUTTONS,
)
from handlers.utils import parse_floor_label, get_rooms_keyboard_by_floor, get_rooms_set_by_floor

logger = logging.getLogger(__name__)

# Простая FSM для сценария "от моего кабинета до другого"
_route_state: Dict[int, Dict[str, Any]] = {}


def is_user_in_route_mode(user_id: int) -> bool:
    """Проверка, находится ли пользователь в режиме маршрута A→B."""
    st = _route_state.get(user_id)
    return st is not None


def _is_route_waiting_floor(message: Message) -> bool:
    """Проверка, ожидает ли бот выбора этажа для маршрута."""
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    st = _route_state.get(user_id)
    if not st:
        return False
    step = st.get("step")
    result = step in {"await_floor_a", "await_floor_b"}
    logger.debug(f"_is_route_waiting_floor: user_id={user_id}, step={step}, result={result}")
    return result


def _is_route_waiting_room(message: Message) -> bool:
    """Проверка, ожидает ли бот выбора кабинета для маршрута."""
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    st = _route_state.get(user_id)
    if not st:
        return False
    return st.get("step") in {"await_room_a", "await_room_b"}


async def on_route_entry(message: Message):
    """Старт сценария A→B."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        _route_state[user_id] = {"step": "await_floor_a"}
        await message.answer("Выберите начальный этаж:", reply_markup=get_floor_selection_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в on_route_entry: {e}", exc_info=True)


async def on_route_floor(message: Message):
    """Обработка выбора этажа в сценарии A→B."""
    logger.info(f"on_route_floor вызван: text={message.text}, user_id={message.from_user.id if message.from_user else None}")
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            logger.warning("on_route_floor: user_id не найден")
            return
        st = _route_state.get(user_id)
        if not st:
            logger.warning(f"on_route_floor: состояние не найдено для user_id={user_id}")
            return
        logger.info(f"on_route_floor: состояние найдено, step={st.get('step')}")
        floor = parse_floor_label(message.text)
        if floor is None:
            logger.warning(f"on_route_floor: не удалось распарсить этаж из '{message.text}'")
            return
        logger.info(f"on_route_floor: распарсен этаж={floor}, step={st.get('step')}")
        if st.get("step") == "await_floor_a":
            st["floor_a"] = floor
            st["step"] = "await_room_a"
            # Правильное склонение для этажа
            if floor == 1:
                floor_text = "1 этажа"
            elif floor == 2:
                floor_text = "2 этажа"
            elif floor == 3:
                floor_text = "3 этажа"
            else:
                floor_text = "4 этажа"
            await message.answer(f"Кабинеты {floor_text}:", reply_markup=get_rooms_keyboard_by_floor(floor))
            return
        if st.get("step") == "await_floor_b":
            st["floor_b"] = floor
            st["step"] = "await_room_b"
            # Правильное склонение для этажа
            if floor == 1:
                floor_text = "1 этажа"
            elif floor == 2:
                floor_text = "2 этажа"
            elif floor == 3:
                floor_text = "3 этажа"
            else:
                floor_text = "4 этажа"
            await message.answer(f"Кабинеты {floor_text}:", reply_markup=get_rooms_keyboard_by_floor(floor))
            return
    except Exception as e:
        logger.error(f"Ошибка в on_route_floor: {e}", exc_info=True)


async def on_route_room(message: Message):
    """Обработка выбора кабинета в сценарии A→B."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        st = _route_state.get(user_id)
        if not st:
            return
        step = st.get("step")
        selected_room = (message.text or "").strip()

        if step == "await_room_a":
            floor_a = st.get("floor_a")
            if not floor_a or selected_room not in get_rooms_set_by_floor(floor_a):
                return
            st["room_a"] = selected_room
            st["step"] = "await_floor_b"
            await message.answer("Выберите конечный этаж:", reply_markup=get_floor_selection_keyboard())
            return

        if step == "await_room_b":
            floor_b = st.get("floor_b")
            if not floor_b or selected_room not in get_rooms_set_by_floor(floor_b):
                return
            
            # Проверяем, что кабинеты разные
            room_a = st.get("room_a", "")
            if selected_room == room_a:
                await message.answer("Выберите другой кабинет для построения маршрута", reply_markup=get_rooms_keyboard_by_floor(floor_b))
                return
            
            st["room_b"] = selected_room
            # Финал сценария
            await message.answer("Здесь Скоро все будет работать")
            await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
            _route_state.pop(user_id, None)
            return
    except Exception as e:
        logger.error(f"Ошибка в on_route_room: {e}", exc_info=True)


def register_route_handlers(dp: Dispatcher):
    """Регистрация обработчиков маршрута A→B."""
    dp.message.register(on_route_entry, F.text == ROUTE_ENTRY_TEXT)
    # A→B: выбор этажа (фильтр только когда мы в сценарии)
    dp.message.register(
        on_route_floor,
        F.text.in_({FLOOR_1_TEXT, FLOOR_2_TEXT, FLOOR_3_TEXT, FLOOR_4_TEXT}),
        _is_route_waiting_floor,
    )
    # A→B: выбор кабинета (фильтр только когда мы в сценарии)
    all_rooms: Set[str] = set().union(
        FIRST_FLOOR_ROOM_BUTTONS,
        SECOND_FLOOR_ROOM_BUTTONS,
        THIRD_FLOOR_ROOM_BUTTONS,
        FOURTH_FLOOR_ROOM_BUTTONS,
    )
    dp.message.register(
        on_route_room,
        F.text.in_(all_rooms),
        _is_route_waiting_room,
    )

