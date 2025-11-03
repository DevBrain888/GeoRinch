"""Обработчики для сценария поиска кабинета"""
import logging
from typing import Dict, Set
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards import (
    get_main_keyboard,
    get_floor_selection_keyboard,
    get_first_floor_rooms_keyboard,
    get_second_floor_rooms_keyboard,
    get_third_floor_rooms_keyboard,
    get_fourth_floor_rooms_keyboard,
)

from handlers.constants import (
    SEARCH_ENTRY_TEXT,
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
from handlers.map import is_user_in_map_mode
from handlers.route import is_user_in_route_mode
from handlers.notifications import add_user_to_main_menu, remove_user_from_main_menu

logger = logging.getLogger(__name__)

# Память последнего выбранного этажа по пользователю для разрешения неоднозначных названий
_user_last_selected_floor: Dict[int, int] = {}


async def on_search_entry(message: Message):
    """Точка входа: пользователь нажимает кнопку "Поиск кабинета"."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if user_id:
            remove_user_from_main_menu(user_id)  # Удаляем из главного меню при входе в поиск
        await message.answer(
            "Выберите этаж:", reply_markup=get_floor_selection_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_search_entry: {e}", exc_info=True)


async def on_floor_1(message: Message):
    """Показать кабинеты 1 этажа."""
    try:
        user_id = message.from_user.id if message.from_user else None
        # Не обрабатываем, если пользователь в режиме карты или маршрута
        if user_id:
            if is_user_in_map_mode(user_id):
                logger.debug(f"on_floor_1: пользователь {user_id} в режиме карты, пропускаем")
                return
            if is_user_in_route_mode(user_id):
                logger.debug(f"on_floor_1: пользователь {user_id} в режиме маршрута, пропускаем")
                return
        if user_id:
            _user_last_selected_floor[user_id] = 1
        await message.answer(
            "Кабинеты 1 этажа:", reply_markup=get_first_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_1: {e}", exc_info=True)


async def on_floor_2(message: Message):
    """Показать кабинеты 2 этажа."""
    try:
        user_id = message.from_user.id if message.from_user else None
        # Не обрабатываем, если пользователь в режиме карты или маршрута
        if user_id and (is_user_in_map_mode(user_id) or is_user_in_route_mode(user_id)):
            return
        if user_id:
            _user_last_selected_floor[user_id] = 2
        await message.answer(
            "Кабинеты 2 этажа:", reply_markup=get_second_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_2: {e}", exc_info=True)


async def on_floor_3(message: Message):
    """Показать кабинеты 3 этажа."""
    try:
        user_id = message.from_user.id if message.from_user else None
        # Не обрабатываем, если пользователь в режиме карты или маршрута
        if user_id and (is_user_in_map_mode(user_id) or is_user_in_route_mode(user_id)):
            return
        if user_id:
            _user_last_selected_floor[user_id] = 3
        await message.answer(
            "Кабинеты 3 этажа:", reply_markup=get_third_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_3: {e}", exc_info=True)


async def on_floor_4(message: Message):
    """Показать кабинеты 4 этажа."""
    try:
        user_id = message.from_user.id if message.from_user else None
        # Не обрабатываем, если пользователь в режиме карты или маршрута
        if user_id and (is_user_in_map_mode(user_id) or is_user_in_route_mode(user_id)):
            return
        if user_id:
            _user_last_selected_floor[user_id] = 4
        await message.answer(
            "Кабинеты 4 этажа:", reply_markup=get_fourth_floor_rooms_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в on_floor_4: {e}", exc_info=True)


async def on_room_selected(message: Message):
    """Отправить картинку выбранного этажа и показать инлайн кнопку добавления в избранное."""
    try:
        selected_text = (message.text or "").strip()
        user_id = message.from_user.id if message.from_user else None
        image_url = None

        # Определяем изображение по последнему выбранному этажу пользователя
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
        # Проверяем длину callback_data (Telegram ограничивает до 64 байт)
        callback_data = f"add_favorite:{selected_text}"
        if len(callback_data.encode('utf-8')) > 64:
            logger.warning(f"callback_data слишком длинный ({len(callback_data.encode('utf-8'))} байт): {callback_data}")
            # Обрезаем до 64 байт
            max_room_len = 64 - len("add_favorite:".encode('utf-8'))
            room_bytes = selected_text.encode('utf-8')[:max_room_len]
            selected_text = room_bytes.decode('utf-8', errors='ignore')
            callback_data = f"add_favorite:{selected_text}"
            logger.info(f"Обрезан callback_data до: {callback_data}")
        
        logger.debug(f"Создание inline кнопки с callback_data='{callback_data}' для room='{selected_text}'")
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Добавить в избранное", callback_data=callback_data)]]
        )
        await message.answer("Добавить в избранное ?", reply_markup=inline_kb)
        
        # Возвращаем пользователя в начальное состояние (главное меню)
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
        # Отслеживаем, что пользователь вернулся в главное меню
        if user_id:
            add_user_to_main_menu(user_id)
        
        # Сбрасываем сохранённый этаж, чтобы не влиять на последующие действия
        if user_id in _user_last_selected_floor:
            del _user_last_selected_floor[user_id]
    except Exception as e:
        logger.error(f"Ошибка в on_room_selected: {e}", exc_info=True)


def register_search_handlers(dp: Dispatcher):
    """Регистрация обработчиков сценария поиска кабинета."""
    # Точка входа обычного поиска
    dp.message.register(on_search_entry, F.text == SEARCH_ENTRY_TEXT)

    # Выбор этажей
    dp.message.register(on_floor_1, F.text == FLOOR_1_TEXT)
    dp.message.register(on_floor_2, F.text == FLOOR_2_TEXT)
    dp.message.register(on_floor_3, F.text == FLOOR_3_TEXT)
    dp.message.register(on_floor_4, F.text == FLOOR_4_TEXT)

    # Выбор кабинетов
    dp.message.register(on_room_selected, F.text.in_(FIRST_FLOOR_ROOM_BUTTONS))
    dp.message.register(on_room_selected, F.text.in_(SECOND_FLOOR_ROOM_BUTTONS))
    dp.message.register(on_room_selected, F.text.in_(THIRD_FLOOR_ROOM_BUTTONS))
    dp.message.register(on_room_selected, F.text.in_(FOURTH_FLOOR_ROOM_BUTTONS))
