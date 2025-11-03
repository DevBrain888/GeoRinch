"""Вспомогательные функции для обработчиков"""
from typing import Optional, Set

from keyboards import (
    get_first_floor_rooms_keyboard,
    get_fourth_floor_rooms_keyboard,
    get_second_floor_rooms_keyboard,
    get_third_floor_rooms_keyboard,
)

from handlers.constants import (
    FLOOR_1_TEXT,
    FLOOR_2_TEXT,
    FLOOR_3_TEXT,
    FLOOR_4_TEXT,
    FIRST_FLOOR_ROOM_BUTTONS,
    SECOND_FLOOR_ROOM_BUTTONS,
    THIRD_FLOOR_ROOM_BUTTONS,
    FOURTH_FLOOR_ROOM_BUTTONS,
    FIRST_FLOOR_ROOM_IMAGE_URL,
    SECOND_FLOOR_ROOM_IMAGE_URL,
    THIRD_FLOOR_ROOM_IMAGE_URL,
    FOURTH_FLOOR_ROOM_IMAGE_URL,
)


def parse_floor_label(text: Optional[str]) -> Optional[int]:
    """Парсит текст этажа и возвращает номер этажа (1-4) или None."""
    t = (text or "").strip()
    if t == FLOOR_1_TEXT:
        return 1
    if t == FLOOR_2_TEXT:
        return 2
    if t == FLOOR_3_TEXT:
        return 3
    if t == FLOOR_4_TEXT:
        return 4
    return None


def get_rooms_keyboard_by_floor(floor: int):
    """Получить клавиатуру кабинетов для указанного этажа."""
    if floor == 1:
        return get_first_floor_rooms_keyboard()
    if floor == 2:
        return get_second_floor_rooms_keyboard()
    if floor == 3:
        return get_third_floor_rooms_keyboard()
    return get_fourth_floor_rooms_keyboard()


def get_rooms_set_by_floor(floor: int) -> Set[str]:
    """Получить множество названий кабинетов для указанного этажа."""
    if floor == 1:
        return FIRST_FLOOR_ROOM_BUTTONS
    if floor == 2:
        return SECOND_FLOOR_ROOM_BUTTONS
    if floor == 3:
        return THIRD_FLOOR_ROOM_BUTTONS
    return FOURTH_FLOOR_ROOM_BUTTONS


def get_floor_image_url(floor: int) -> Optional[str]:
    """Получить URL изображения для указанного этажа."""
    if floor == 1:
        return FIRST_FLOOR_ROOM_IMAGE_URL
    if floor == 2:
        return SECOND_FLOOR_ROOM_IMAGE_URL
    if floor == 3:
        return THIRD_FLOOR_ROOM_IMAGE_URL
    if floor == 4:
        return FOURTH_FLOOR_ROOM_IMAGE_URL
    return None

