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


def get_floor_selection_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора этажа (пока функционален только 1 этаж)."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 этаж"), KeyboardButton(text="2 этаж")],
            [KeyboardButton(text="3 этаж"), KeyboardButton(text="4 этаж")],
        ],
        resize_keyboard=True
    )
    return keyboard


def get_first_floor_rooms_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура кабинетов 1 этажа. Каждая кнопка на всю ширину (отдельная строка)."""
    room_buttons = [
        "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111",
        "Охрана", "Гардероб", "Туалет", "Канцелярия", "Каб. Воспитательной работы", "Каб. Директора",
    ]
    keyboard_layout = [[KeyboardButton(text=label)] for label in room_buttons]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_layout,
        resize_keyboard=True
    )
    return keyboard


def get_second_floor_rooms_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура кабинетов 2 этажа. Каждая кнопка на всю ширину (отдельная строка)."""
    room_buttons = [
        "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", 
        "212", "213", "214", "215", "216", "217", "218", "Мужской Туалет", "Женский Туалет"
    ]
    keyboard_layout = [[KeyboardButton(text=label)] for label in room_buttons]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_layout,
        resize_keyboard=True
    )
    return keyboard


def get_third_floor_rooms_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура кабинетов 3 этажа. Каждая кнопка на всю ширину (отдельная строка)."""
    room_buttons = [
        "301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311", 
        "Актовый Зал", "Мужской Туалет", "Женский Туалет"
    ]
    keyboard_layout = [[KeyboardButton(text=label)] for label in room_buttons]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_layout,
        resize_keyboard=True
    )
    return keyboard


def get_fourth_floor_rooms_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура кабинетов 4 этажа. Каждая кнопка на всю ширину (отдельная строка)."""
    room_buttons = [
        "403", "404", "405", "406", "407", "Каб. Психолога", "Мужской Туалет", "Женский Туалет"
    ]
    keyboard_layout = [[KeyboardButton(text=label)] for label in room_buttons]
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_layout,
        resize_keyboard=True
    )
    return keyboard

