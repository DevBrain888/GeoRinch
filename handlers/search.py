"""Обработчики для сценария "Поиск кабинета"""
import logging
from typing import Dict
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


logger = logging.getLogger(__name__)


SEARCH_ENTRY_TEXT = "Поиск кабинета"
FLOOR_1_TEXT = "1 этаж"
FLOOR_2_TEXT = "2 этаж"
FLOOR_3_TEXT = "3 этаж"
FLOOR_4_TEXT = "4 этаж"

# URL изображения, отправляемого при выборе кабинета
FIRST_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/tMvhp5nz/1Floor.jpg"
SECOND_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/TDKqpQzb/2Floor.jpg"
THIRD_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/sv6XhMnS/3Floor.jpg"
FOURTH_FLOOR_ROOM_IMAGE_URL = "https://i.ibb.co/DDpVqcFP/4Floor.jpg"

# Память последнего выбранного этажа по пользователю для разрешения неоднозначных названий
_user_last_selected_floor: Dict[int, int] = {}


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


def register_search_handlers(dp: Dispatcher):
    """Регистрация обработчиков сценария поиска кабинета."""
    # Точка входа
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


