"""Обработчики для периодических уведомлений"""
import asyncio
import logging
import random
from typing import Dict, Set
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import Message

logger = logging.getLogger(__name__)

# Текст уведомления о запрете курения
SMOKING_BAN_NOTIFICATION = (
    "🚭 Напоминание: Запрещено курить возле колледжа и прокуратуры!"
)

# Множество пользователей, которые находятся в главном меню
_users_in_main_menu: Set[int] = set()

# Словарь для хранения времени последнего уведомления для каждого пользователя
_last_notification_time: Dict[int, datetime] = {}

# Минимальный и максимальный интервал между уведомлениями (в секундах)
MIN_INTERVAL = 300  # 5 минут
MAX_INTERVAL = 1800  # 30 минут


def add_user_to_main_menu(user_id: int):
    """Добавить пользователя в множество тех, кто находится в главном меню."""
    _users_in_main_menu.add(user_id)
    logger.debug(f"Пользователь {user_id} добавлен в главное меню (всего: {len(_users_in_main_menu)})")


def remove_user_from_main_menu(user_id: int):
    """Удалить пользователя из множества тех, кто находится в главном меню."""
    _users_in_main_menu.discard(user_id)
    logger.debug(f"Пользователь {user_id} удален из главного меню (всего: {len(_users_in_main_menu)})")


def is_user_in_main_menu(user_id: int) -> bool:
    """Проверить, находится ли пользователь в главном меню."""
    return user_id in _users_in_main_menu


async def send_notification_to_user(bot: Bot, user_id: int):
    """Отправить уведомление о запрете курения пользователю."""
    try:
        await bot.send_message(user_id, SMOKING_BAN_NOTIFICATION)
        _last_notification_time[user_id] = datetime.now()
        logger.info(f"Отправлено уведомление о запрете курения пользователю {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}", exc_info=True)
        # Если пользователь заблокировал бота или произошла ошибка, удаляем его из списка
        remove_user_from_main_menu(user_id)


def should_send_notification(user_id: int) -> bool:
    """Проверить, нужно ли отправить уведомление пользователю."""
    if not is_user_in_main_menu(user_id):
        return False
    
    last_time = _last_notification_time.get(user_id)
    if last_time is None:
        # Первое уведомление - отправим через случайный интервал
        return True
    
    # Вычисляем случайный интервал для этого пользователя
    elapsed = (datetime.now() - last_time).total_seconds()
    interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
    
    return elapsed >= interval


async def notification_worker(bot: Bot):
    """Фоновая задача для отправки периодических уведомлений."""
    logger.info("Запущен воркер периодических уведомлений")
    
    while True:
        try:
            # Проверяем всех пользователей в главном меню
            users_to_notify = []
            for user_id in list(_users_in_main_menu):
                if should_send_notification(user_id):
                    users_to_notify.append(user_id)
            
            # Отправляем уведомления
            for user_id in users_to_notify:
                await send_notification_to_user(bot, user_id)
                # Небольшая задержка между отправками, чтобы не перегружать API
                await asyncio.sleep(0.5)
            
            # Ждем перед следующей проверкой (проверяем каждую минуту)
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Ошибка в notification_worker: {e}", exc_info=True)
            await asyncio.sleep(60)


async def track_main_menu_entry(message: Message):
    """Отслеживать вход пользователя в главное меню."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if user_id:
            add_user_to_main_menu(user_id)
    except Exception as e:
        logger.error(f"Ошибка в track_main_menu_entry: {e}", exc_info=True)


async def on_startup(dispatcher):
    """Хук запуска, вызывается при старте бота."""
    logger.info("Запуск воркера периодических уведомлений...")
    # Получаем bot из dispatcher
    bot = dispatcher.bot
    asyncio.create_task(notification_worker(bot))
    logger.info("Воркер периодических уведомлений запущен")


def register_notification_handlers(dp, bot: Bot):
    """Регистрация обработчиков уведомлений."""
    # Регистрируем хук запуска для polling режима
    # В aiogram 3.x startup хуки принимают dispatcher
    dp.startup.register(on_startup)
    logger.info("Зарегистрированы обработчики уведомлений")

