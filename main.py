"""Точка входа для запуска Telegram бота"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

import config
from handlers import register_error_handler, register_start_handler

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
logger.info("Инициализация бота...")
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Регистрируем все обработчики
register_error_handler(dp)
register_start_handler(dp)


async def main():
    try:
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        # Игнорируем CancelledError при корректном завершении
        logger.info("Получен сигнал отмены, завершение работы...")
        pass
    except Exception as e:
        logger.error(f"Критическая ошибка в main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("Запуск Telegram бота")
        logger.info("=" * 50)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения (Ctrl+C)")
        print("\nБот успешно остановлен.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)
        sys.exit(1)
