"""Обработчик ошибок"""
import sys
import logging
from aiogram import Dispatcher
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)


async def error_handler(event: ErrorEvent):
    """
    Глобальный обработчик ошибок.
    Логирует все ошибки, но не отправляет их пользователю.
    """
    try:
        exception = event.exception
        update = event.update
        
        # Получаем информацию о пользователе и чате из update
        user_id = None
        chat_id = None
        
        try:
            if hasattr(update, 'message') and update.message:
                user_id = update.message.from_user.id if update.message.from_user else None
                chat_id = update.message.chat.id if update.message.chat else None
            elif hasattr(update, 'callback_query') and update.callback_query:
                if update.callback_query.from_user:
                    user_id = update.callback_query.from_user.id
                if update.callback_query.message and update.callback_query.message.chat:
                    chat_id = update.callback_query.message.chat.id
        except Exception:
            # Игнорируем ошибки при получении информации о пользователе
            pass
        
        logger.error(
            f"Ошибка в обработчике: {type(exception).__name__}: {str(exception)}",
            exc_info=True,
            extra={
                "user_id": user_id,
                "chat_id": chat_id,
            }
        )
    except Exception as log_error:
        # Если логирование само вызвало ошибку, выводим в консоль без использования logger
        print(f"Критическая ошибка в обработчике ошибок: {log_error}", file=sys.stderr)
        print(f"Исходная ошибка: {type(event.exception).__name__}: {event.exception}", file=sys.stderr)
    
    # Возвращаем None, чтобы не отправлять ошибку пользователю
    return None


def register_error_handler(dp: Dispatcher):
    """Регистрирует обработчик ошибок"""
    dp.error.register(error_handler)

