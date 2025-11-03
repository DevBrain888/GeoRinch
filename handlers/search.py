"""Обработчики для сценариев поиска и маршрута A→B"""
import logging
from typing import Dict, Any, Optional, Set
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import (
    get_main_keyboard,
    get_floor_selection_keyboard,
    get_first_floor_rooms_keyboard,
    get_second_floor_rooms_keyboard,
    get_third_floor_rooms_keyboard,
    get_fourth_floor_rooms_keyboard,
    get_place_guide,
)


logger = logging.getLogger(__name__)


SEARCH_ENTRY_TEXT = "Поиск кабинета"
ROUTE_ENTRY_TEXT = "Как пройти от моего кабинета до другого"
MAP_ENTRY_TEXT = "Карта колледжа"
GUIDE_ENTRY_TEXT = "Справочник"
GUIDE_SHOP_TEXT = "Магазин пятерочка"
GUIDE_APTEKA_TEXT = "Аптека"
FLOOR_1_TEXT = "1 этаж"
FLOOR_2_TEXT = "2 этаж"
FLOOR_3_TEXT = "3 этаж"
FLOOR_4_TEXT = "4 этаж"

# URL изображения, отправляемого при выборе кабинета
FIRST_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/tMvhp5nz/1Floor.jpg"
SECOND_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/TDKqpQzb/2Floor.jpg"
THIRD_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/sv6XhMnS/3Floor.jpg"
FOURTH_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/DDpVqcFP/4Floor.jpg"

# URL изображения, отправляемого при выборе метса
GUIDE_SHOP = "https://i.ibb.co/tjcVCG1/guide-apteka.png"
GUIDE_APTEKA = "https://i.ibb.co/5hvtkHdZ/guide-shop.png"


# Память последнего выбранного этажа по пользователю для разрешения неоднозначных названий
_user_last_selected_floor: Dict[int, int] = {}

# Простая FSM для сценария "от моего кабинета до другого"
_route_state: Dict[int, Dict[str, Any]] = {}

# Простая FSM для сценария "Карта колледжа"
_map_state: Dict[int, Dict[str, Any]] = {}


def _parse_floor_label(text: Optional[str]) -> Optional[int]:
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


def _get_rooms_keyboard_by_floor(floor: int):
    if floor == 1:
        return get_first_floor_rooms_keyboard()
    if floor == 2:
        return get_second_floor_rooms_keyboard()
    if floor == 3:
        return get_third_floor_rooms_keyboard()
    return get_fourth_floor_rooms_keyboard()


def _get_rooms_set_by_floor(floor: int) -> Set[str]:
    if floor == 1:
        return FIRST_FLOOR_ROOM_BUTTONS
    if floor == 2:
        return SECOND_FLOOR_ROOM_BUTTONS
    if floor == 3:
        return THIRD_FLOOR_ROOM_BUTTONS
    return FOURTH_FLOOR_ROOM_BUTTONS


def _get_floor_image_url(floor: int) -> Optional[str]:
    if floor == 1:
        return FIRST_FLOOR_ROOM_IMAGE_URL
    if floor == 2:
        return SECOND_FLOOR_ROOM_IMAGE_URL
    if floor == 3:
        return THIRD_FLOOR_ROOM_IMAGE_URL
    if floor == 4:
        return FOURTH_FLOOR_ROOM_IMAGE_URL
    return None


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


def _is_map_waiting_floor(message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    st = _map_state.get(user_id)
    if not st:
        return False
    return st.get("step") == "await_floor"


async def on_map_floor(message: Message):
    """Обработка выбора этажа для карты."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        st = _map_state.get(user_id)
        if not st:
            return
        floor = _parse_floor_label(message.text)
        if floor is None:
            return
        image_url = _get_floor_image_url(floor)
        if image_url:
            await message.answer_photo(photo=image_url)
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
        _map_state.pop(user_id, None)
    except Exception as e:
        logger.error(f"Ошибка в on_map_floor: {e}", exc_info=True)


async def on_guide_entry(message: Message):
    """Старт сценария Справочник."""
    try:
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
    except Exception as e:
        logger.error(f"Ошибка в on_guide_select: {e}", exc_info=True)



async def on_route_entry(message: Message):
    """Старт сценария A→B."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        _route_state[user_id] = {"step": "await_floor_a"}
        await message.answer("Выберите этаж A:", reply_markup=get_floor_selection_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в on_route_entry: {e}", exc_info=True)


def _is_route_waiting_floor(message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    st = _route_state.get(user_id)
    if not st:
        return False
    return st.get("step") in {"await_floor_a", "await_floor_b"}


async def on_route_floor(message: Message):
    """Обработка выбора этажа в сценарии A→B."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        st = _route_state.get(user_id)
        if not st:
            return
        floor = _parse_floor_label(message.text)
        if floor is None:
            return
        if st.get("step") == "await_floor_a":
            st["floor_a"] = floor
            st["step"] = "await_room_a"
            await message.answer("Выберите кабинет A:", reply_markup=_get_rooms_keyboard_by_floor(floor))
            return
        if st.get("step") == "await_floor_b":
            st["floor_b"] = floor
            st["step"] = "await_room_b"
            await message.answer("Выберите кабинет B:", reply_markup=_get_rooms_keyboard_by_floor(floor))
            return
    except Exception as e:
        logger.error(f"Ошибка в on_route_floor: {e}", exc_info=True)


def _is_route_waiting_room(message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return False
    st = _route_state.get(user_id)
    if not st:
        return False
    return st.get("step") in {"await_room_a", "await_room_b"}


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
            if not floor_a or selected_room not in _get_rooms_set_by_floor(floor_a):
                return
            st["room_a"] = selected_room
            st["step"] = "await_floor_b"
            await message.answer("Выберите этаж B:", reply_markup=get_floor_selection_keyboard())
            return

        if step == "await_room_b":
            floor_b = st.get("floor_b")
            if not floor_b or selected_room not in _get_rooms_set_by_floor(floor_b):
                return
            st["room_b"] = selected_room
            # Финал сценария
            await message.answer("Скоро здесь будет все работать")
            await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
            _route_state.pop(user_id, None)
            return
    except Exception as e:
        logger.error(f"Ошибка в on_route_room: {e}", exc_info=True)


async def on_search_entry(message: Message):
    """Точка входа: пользователь нажимает кнопку "Поиск кабинета"."""
    try:
        await message.answer(
            "Выберите этаж:", reply_markup=get_floor_selection_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_search_entry: {e}", exc_info=True)


async def on_floor_1(message: Message): #1 этаж
    """Показать кабинеты 1 этажа (каждая кнопка на всю ширину)."""
    try:
        if message.from_user and message.from_user.id:
            _user_last_selected_floor[message.from_user.id] = 1
        await message.answer(
            "Кабинеты 1 этажа:", reply_markup=get_first_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_1: {e}", exc_info=True)


async def on_floor_2(message: Message): #2 этаж
    """Показать кабинеты 2 этажа (каждая кнопка на всю ширину)."""
    try:
        if message.from_user and message.from_user.id:
            _user_last_selected_floor[message.from_user.id] = 2
        await message.answer(
            "Кабинеты 2 этажа:", reply_markup=get_second_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_2: {e}", exc_info=True)

async def on_floor_3(message: Message): #3 этаж
    """Показать кабинеты 3 этажа (каждая кнопка на всю ширину)."""
    try:
        if message.from_user and message.from_user.id:
            _user_last_selected_floor[message.from_user.id] = 3
        await message.answer(
            "Кабинеты 3 этажа:", reply_markup=get_third_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_3: {e}", exc_info=True)

async def on_floor_4(message: Message): #4 этаж
    """Показать кабинеты 4 этажа (каждая кнопка на всю ширину)."""
    try:
        if message.from_user and message.from_user.id:
            _user_last_selected_floor[message.from_user.id] = 4
        await message.answer(
            "Кабинеты 4 этажа:", reply_markup=get_fourth_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_4: {e}", exc_info=True)


async def on_floor_other_soon(message: Message):
    """Заглушка для неготовых этажей."""
    try:
        await message.answer(
            "Скоро будет доступно. Пока выберите \"1 или 2 этаж\".",
            reply_markup=get_floor_selection_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_other_soon: {e}", exc_info=True)


# Список кнопок кабинетов 1 этажа, на которые реагируем одинаково
FIRST_FLOOR_ROOM_BUTTONS = {
    "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111",
    "Охрана", "Гардероб", "Туалет", "Канцелярия", "Каб. Воспитательной работы", "Каб. Директора",
}

# Список кнопок кабинетов 2 этажа, на которые реагируем одинаково
SECOND_FLOOR_ROOM_BUTTONS = {
    "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", 
    "212", "213", "214", "215", "216", "217", "218", "Мужской Туалет", "Женский Туалет"
}

# Список кнопок кабинетов 3 этажа, на которые реагируем одинаково
THIRD_FLOOR_ROOM_BUTTONS = {
    "301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311", 
    "Актовый Зал", "Мужской Туалет", "Женский Туалет"
}

# Список кнопок кабинетов 4 этажа, на которые реагируем одинаково
FOURTH_FLOOR_ROOM_BUTTONS = {
    "403", "404", "405", "406", "407", "Каб. Психолога", "Мужской Туалет", "Женский Туалет"
}


async def on_room_selected(message: Message):
    """Отправить картинку выбранного этажа и показать инлайн кнопку добавления в избранное."""
    try:
        # Определяем изображение: сначала по последнему выбранному этажу пользователя (если он есть)
        selected_text = (message.text or "").strip()
        user_id = message.from_user.id if message.from_user else None
        image_url = None

        last_floor = _user_last_selected_floor.get(user_id) if user_id else None
        if last_floor == 1:
            image_url = FIRST_FLOOR_ROOM_IMAGE_URL
        elif last_floor == 2:
            image_url = SECOND_FLOOR_ROOM_IMAGE_URL
        elif last_floor == 3:
            image_url = THIRD_FLOOR_ROOM_IMAGE_URL
        elif last_floor == 4:
            image_url = FOURTH_FLOOR_ROOM_IMAGE_URL
        else:
            # Fallback: определяем по наборам кнопок (на случай, если нет состояния)
            if selected_text in SECOND_FLOOR_ROOM_BUTTONS:
                image_url = SECOND_FLOOR_ROOM_IMAGE_URL
            elif selected_text in THIRD_FLOOR_ROOM_BUTTONS:
                image_url = THIRD_FLOOR_ROOM_IMAGE_URL
            elif selected_text in FOURTH_FLOOR_ROOM_BUTTONS:
                image_url = FOURTH_FLOOR_ROOM_IMAGE_URL
            else:
                image_url = FIRST_FLOOR_ROOM_IMAGE_URL

        # Отправляем изображение соответствующего этажа
        await message.answer_photo(photo=image_url)
        # Сообщение с инлайн-кнопкой "Добавить в избранное"
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Добавить в избранное", callback_data="add_favorite")]]
        )
        await message.answer("Добавить в избранное ?", reply_markup=inline_kb)
        # Возвращаем пользователя в начальное состояние (главное меню)
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
        # Сбрасываем сохранённый этаж, чтобы не влиять на последующие действия
        if user_id in _user_last_selected_floor:
            del _user_last_selected_floor[user_id]
    except Exception as e:
        logger.error(f"Ошибка в on_room_selected: {e}", exc_info=True)


async def search_cabinet_a_to_b(message: Message):
    """Поиск кабинета от A до B"""
    try:
        # Устаревший обработчик-заглушка. Перенаправляем в новый сценарий.
        await on_route_entry(message)
    except Exception as e:
        logger.error(f"Ошибка в search_cabinet_a_to_b: {e}", exc_info=True)


async def  map_colleage(message: Message):
    """Карта колледжа"""
    try:
        await message.answer("Карта колледжа")
    except Exception as e:
        logger.error(f"Ошибка в map_colleage: {e}", exc_info=True)



def register_search_handlers(dp: Dispatcher):
    """Регистрация обработчиков сценария поиска кабинета."""
    # Точка входа (Карта колледжа)
    dp.message.register(on_map_entry, F.text == MAP_ENTRY_TEXT)
    dp.message.register(
        on_map_floor,
        F.text.in_({FLOOR_1_TEXT, FLOOR_2_TEXT, FLOOR_3_TEXT, FLOOR_4_TEXT}),
        _is_map_waiting_floor,
    )

    # Точка входа (Справочник) и выбор
    dp.message.register(on_guide_entry, F.text == GUIDE_ENTRY_TEXT)
    dp.message.register(
        on_guide_select,
        F.text.in_({GUIDE_SHOP_TEXT, GUIDE_APTEKA_TEXT}),
    )

    # Точка входа (A→B)
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

    # Точка входа обычного поиска
    dp.message.register(on_search_entry, F.text == SEARCH_ENTRY_TEXT)

    # Выбор этажей
    dp.message.register(on_floor_1, F.text == FLOOR_1_TEXT)
    dp.message.register(on_floor_2, F.text == FLOOR_2_TEXT)
    dp.message.register(on_floor_3, F.text == FLOOR_3_TEXT)
    dp.message.register(on_floor_4, F.text == FLOOR_4_TEXT)

    # Выбор кабинета 1 этажа
    dp.message.register(on_room_selected, F.text.in_(FIRST_FLOOR_ROOM_BUTTONS))
    dp.message.register(on_room_selected, F.text.in_(SECOND_FLOOR_ROOM_BUTTONS))
    dp.message.register(on_room_selected, F.text.in_(THIRD_FLOOR_ROOM_BUTTONS))
    dp.message.register(on_room_selected, F.text.in_(FOURTH_FLOOR_ROOM_BUTTONS))


