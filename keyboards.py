"""Клавиатуры бота"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает главную клавиатуру бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Поиск кабинета"),
                KeyboardButton(text="Как пройти от моего кабинета до другого")
            ],
            [
                KeyboardButton(text="Карта колледжа"),
                KeyboardButton(text="Справочник")
            ],
            [
                KeyboardButton(text="Избранное")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

