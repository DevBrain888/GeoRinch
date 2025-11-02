import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ErrorEvent, ReplyKeyboardMarkup, KeyboardButton

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"bot_{datetime.now().strftime('%Y%m%d')}.log"

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    error_msg = "BOT_TOKEN не найден в переменных окружения! Убедитесь, что файл .env существует и содержит BOT_TOKEN=ваш_токен"
    logger.error(error_msg)
    raise ValueError(error_msg)

logger.info("Инициализация бота...")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Обработчик всех ошибок - логирует ошибки, но не отправляет их пользователю
@dp.error()
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


# Создаем клавиатуру с reply кнопками
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


@dp.message(CommandStart())
async def cmd_start(message: Message):
    try:
        logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
        welcome_text = """Добро пожаловать в бота Карта ФЭК РГЭУ (РИНХ 🗺)!

😎Здесь вы сможете найти нужный вам кабинет и ориентироваться по колледжу

Для начала работы выберите нужный режим на клавиатуре ниже: 

- Поиск кабинета❓
- Карта колледжа🗺
- Как пройти от моего кабинета до другого
- Справочник✏️
- Избранное⭐️

Внимание! Бот находиться на стадий тестирования, поэтому могут быть небольшие ошибки или неточности."""
        await message.answer(welcome_text)
        await message.answer("Выберите режим:", reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в обработчике cmd_start: {e}", exc_info=True)
        # Не отправляем ошибку пользователю, только логируем


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
