"""Обработка вебхуков Telegram для интеграции с FastAPI"""
import logging
from typing import Set
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher
from aiogram.types import Update

import config

logger = logging.getLogger(__name__)

# Хранилище обработанных update_id для защиты от повторной обработки команд
# Структура: {update_id: timestamp}
# Очищается автоматически от старых записей (>5 минут)
_processed_updates: dict[int, datetime] = {}

# Глобальные объекты бота и диспетчера (инициализируются из main.py)
bot: Bot = None
dp: Dispatcher = None


def init_webhook_handler(bot_instance: Bot, dispatcher_instance: Dispatcher):
    """
    Инициализация вебхук-обработчика.
    
    Эта функция должна быть вызвана из main.py после создания bot и dp,
    чтобы передать их в модуль вебхук-обработки.
    
    Args:
        bot_instance: Экземпляр Bot из aiogram
        dispatcher_instance: Экземпляр Dispatcher из aiogram
    """
    global bot, dp
    bot = bot_instance
    dp = dispatcher_instance
    logger.info("Вебхук-обработчик инициализирован")


def _cleanup_old_updates():
    """
    Очистка старых update_id из кэша.
    
    Удаляет записи старше 5 минут для предотвращения роста памяти.
    Эта функция вызывается автоматически при каждом новом обновлении.
    """
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=5)
    
    # Удаляем старые записи
    old_updates = [
        update_id for update_id, timestamp in _processed_updates.items()
        if timestamp < cutoff_time
    ]
    
    for update_id in old_updates:
        del _processed_updates[update_id]
    
    if old_updates:
        logger.debug(f"Очищено {len(old_updates)} старых update_id из кэша")


async def process_webhook_update(token: str, update_data: dict, request: Request):
    """
    Обработка входящего обновления от Telegram через вебхук.
    
    Интеграция вебхук-обработки:
    1. Telegram отправляет POST запрос на /webhook/{token} с JSON-данными Update
    2. Функция проверяет токен на соответствие BOT_TOKEN из config
    3. Проверяется update_id на дубликаты (защита от повторной обработки)
    4. Update преобразуется в объект aiogram.types.Update
    5. Update передаётся в Dispatcher для обработки через зарегистрированные handlers
    6. Возвращается успешный ответ Telegram API
    
    Логика проверки повторных команд:
    - Каждое обновление от Telegram имеет уникальный update_id
    - Telegram может повторно отправить обновление при таймауте или сетевых проблемах
    - Мы сохраняем update_id с timestamp в памяти (_processed_updates)
    - При получении обновления проверяем, не обрабатывали ли мы его ранее
    - Если update_id уже есть в кэше - игнорируем обновление (idempotency)
    - Старые записи (>5 минут) автоматически очищаются для экономии памяти
    
    Args:
        token: Токен бота из URL пути (для проверки безопасности)
        update_data: JSON данные обновления от Telegram
        request: FastAPI Request объект (для логирования IP адреса)
    
    Returns:
        JSONResponse со статусом OK для Telegram API
    
    Raises:
        HTTPException: Если токен неверный или данные обновления некорректны
    """
    # Проверка токена для безопасности endpoint
    if token != config.BOT_TOKEN:
        logger.warning(
            f"Попытка доступа с неверным токеном. IP: {request.client.host if request.client else 'unknown'}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
    
    try:
        # Преобразуем JSON в объект Update aiogram
        update = Update(**update_data)
        
        # Логика проверки повторных команд (idempotency)
        update_id = update.update_id
        
        # Очищаем старые записи периодически
        _cleanup_old_updates()
        
        # Проверяем, не обрабатывали ли мы это обновление ранее
        if update_id in _processed_updates:
            logger.debug(
                f"Получено повторное обновление update_id={update_id}, "
                f"оригинальное время обработки: {_processed_updates[update_id]}"
            )
            # Возвращаем успешный ответ, но не обрабатываем повторно
            # Это гарантирует idempotency и предотвращает дублирование действий
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"ok": True, "duplicate": True}
            )
        
        # Сохраняем update_id с текущим временем
        _processed_updates[update_id] = datetime.now()
        
        # Логируем получение обновления
        logger.debug(
            f"Получено новое обновление update_id={update_id} "
            f"от IP: {request.client.host if request.client else 'unknown'}"
        )
        
        # Передаём обновление в Dispatcher для обработки
        # Dispatcher автоматически вызывает соответствующие handlers
        # на основе типов обновления (Message, CallbackQuery и т.д.)
        await dp.feed_update(bot, update)
        
        # Возвращаем успешный ответ Telegram API
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True}
        )
        
    except Exception as e:
        logger.error(
            f"Ошибка при обработке вебхук обновления: {e}",
            exc_info=True,
            extra={"update_data": update_data}
        )
        # Все равно возвращаем 200 OK, чтобы Telegram не повторял запрос
        # Ошибки уже залогированы через error_handler в handlers/errors.py
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": False, "error": "Internal processing error"}
        )


def create_webhook_app(bot_instance: Bot, dispatcher_instance: Dispatcher) -> FastAPI:
    """
    Создаёт FastAPI приложение с endpoint для вебхуков.
    
    Используется для интеграции aiogram Dispatcher с FastAPI.
    После создания приложения его нужно запустить через uvicorn.
    
    Args:
        bot_instance: Экземпляр Bot из aiogram
        dispatcher_instance: Экземпляр Dispatcher из aiogram
    
    Returns:
        FastAPI приложение с зарегистрированным endpoint /webhook/{token}
    """
    # Инициализируем глобальные переменные
    init_webhook_handler(bot_instance, dispatcher_instance)
    
    # Создаём FastAPI приложение
    app = FastAPI(
        title="Telegram Bot Webhook",
        description="Вебхук endpoint для Telegram бота"
    )
    
    # Регистрируем endpoint для приёма обновлений от Telegram
    # Telegram отправляет POST запросы на этот URL с JSON данными Update
    @app.post("/webhook/{token}")
    async def webhook_endpoint(token: str, request: Request):
        """
        Endpoint для приёма обновлений от Telegram.
        
        Telegram API отправляет обновления на этот endpoint методом POST.
        Путь содержит токен бота для базовой безопасности endpoint.
        """
        # Получаем JSON данные из тела запроса
        update_data = await request.json()
        
        # Обрабатываем обновление
        return await process_webhook_update(token, update_data, request)
    
    # Healthcheck endpoint для мониторинга
    @app.get("/health")
    async def health_check():
        """Endpoint для проверки работоспособности сервиса"""
        return {"status": "ok", "service": "telegram-bot-webhook"}
    
    logger.info("FastAPI приложение создано с endpoint /webhook/{token}")
    
    return app

