"""Точка входа для запуска Telegram бота"""
import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

import config
from handlers import register_error_handler, register_start_handler
from webhook_handler import create_webhook_app

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
logger.info("Инициализация бота...")
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Регистрируем все обработчики
register_error_handler(dp)
register_start_handler(dp)


async def main_polling():
    """
    Запуск бота в режиме polling (long polling).
    
    Используется для разработки и тестирования.
    Бот сам запрашивает обновления у Telegram API.
    """
    try:
        logger.info("Запуск бота в режиме polling...")
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        # Игнорируем CancelledError при корректном завершении
        logger.info("Получен сигнал отмены, завершение работы...")
        pass
    except Exception as e:
        logger.error(f"Критическая ошибка в main_polling: {e}", exc_info=True)
        raise


def main_webhook():
    """
    Запуск бота в режиме webhook через FastAPI.
    
    В этом режиме Telegram отправляет обновления на наш сервер.
    Требует настройки вебхука через setWebhook в Telegram API.
    Используется для production окружения.
    """
    try:
        try:
            import uvicorn
        except ImportError:
            logger.error(
                "uvicorn не установлен. Установите его через: pip install uvicorn fastapi"
            )
            raise
        
        # Получаем настройки из переменных окружения (используем существующий .env)
        webhook_host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
        webhook_port = int(os.getenv("WEBHOOK_PORT", "8000"))
        
        # Создаём FastAPI приложение с вебхук endpoint
        app = create_webhook_app(bot, dp)
        
        logger.info(f"Запуск FastAPI сервера на {webhook_host}:{webhook_port}")
        logger.info(f"Вебхук endpoint: http://{webhook_host}:{webhook_port}/webhook/{config.BOT_TOKEN}")
        logger.info("Не забудьте настроить вебхук через setWebhook в Telegram API!")
        
        # Запускаем FastAPI приложение через uvicorn
        uvicorn.run(
            app,
            host=webhook_host,
            port=webhook_port,
            log_level="info"
        )
    except Exception as e:
        logger.critical(f"Критическая ошибка в main_webhook: {e}", exc_info=True)
        raise


async def main():
    """
    Основная функция запуска.
    
    Выбирает режим работы на основе переменной окружения USE_WEBHOOK.
    Если USE_WEBHOOK=true или 1 - запускается webhook режим,
    иначе - polling режим (по умолчанию для обратной совместимости).
    """
    use_webhook = os.getenv("USE_WEBHOOK", "").lower() in ("true", "1", "yes")
    
    if use_webhook:
        logger.info("Режим работы: WEBHOOK")
        # Для webhook используем синхронный запуск через uvicorn
        main_webhook()
    else:
        logger.info("Режим работы: POLLING")
        await main_polling()


if __name__ == "__main__":
    try:
        logger.info("=" * 50)
        logger.info("Запуск Telegram бота")
        logger.info("=" * 50)
        
        # Проверяем режим работы
        use_webhook = os.getenv("USE_WEBHOOK", "").lower() in ("true", "1", "yes")
        
        if use_webhook:
            # Webhook режим запускается синхронно
            main_webhook()
        else:
            # Polling режим запускается асинхронно
            asyncio.run(main())
            
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения (Ctrl+C)")
        print("\nБот успешно остановлен.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)
        sys.exit(1)
