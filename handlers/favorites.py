"""Обработчики для функционала избранного"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from keyboards import get_main_keyboard
from handlers.constants import FAVORITES_ENTRY_TEXT
from handlers.db.favorites import add_favorite, remove_favorite, list_favorites

logger = logging.getLogger(__name__)


async def debug_callback_handler(callback: CallbackQuery):
    """Отладочный обработчик для всех callback queries."""
    logger.info(f"DEBUG: Получен callback query! data='{callback.data}', user_id={callback.from_user.id if callback.from_user else None}")
    # Не отвечаем здесь, чтобы не мешать другим обработчикам


async def on_favorites_entry(message: Message):
    """Показать избранные кабинеты пользователя."""
    try:
        user_id = message.from_user.id if message.from_user else None
        if not user_id:
            return
        rooms = list_favorites(user_id)
        if not rooms:
            await message.answer("Избранное пусто.", reply_markup=get_main_keyboard())
            return
        kb_rows = [
            [InlineKeyboardButton(text=f"{room} ❌", callback_data=f"del_favorite:{room}")]
            for room in rooms
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
        await message.answer("Ваши избраные кабинеты", reply_markup=inline_kb)
    except Exception as e:
        logger.error(f"Ошибка в on_favorites_entry: {e}", exc_info=True)


async def on_add_favorite_callback(callback: CallbackQuery):
    """Добавление кабинета в избранное (инлайн-кнопка)."""
    logger.info(f"on_add_favorite_callback вызван! callback.data = {callback.data}, user_id = {callback.from_user.id if callback.from_user else None}")
    try:
        user_id = callback.from_user.id if callback.from_user else None
        if not user_id:
            logger.warning(f"on_add_favorite_callback: user_id не найден")
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        data = callback.data or ""
        logger.info(f"on_add_favorite_callback: обработка callback.data = '{data}', user_id = {user_id}")
        
        # ожидаем формат: add_favorite:ROOM
        if not data.startswith("add_favorite:"):
            logger.warning(f"on_add_favorite_callback: неверный формат данных: {data}")
            await callback.answer("Неверный формат данных", show_alert=True)
            return
            
        parts = data.split(":", 1)
        room = parts[1].strip() if len(parts) == 2 else ""
        
        if not room:
            logger.warning(f"on_add_favorite_callback: не удалось извлечь room из {data}")
            await callback.answer("Не удалось определить кабинет", show_alert=True)
            return
        
        logger.info(f"on_add_favorite_callback: добавление room='{room}' для user_id={user_id}")
        success = add_favorite(user_id, room)
        if success:
            logger.info(f"on_add_favorite_callback: успешно добавлено room='{room}' для user_id={user_id}")
            await callback.answer("Добавлено в избранное", show_alert=False)
        else:
            logger.error(f"on_add_favorite_callback: ошибка при добавлении room='{room}' для user_id={user_id}")
            await callback.answer("Ошибка при добавлении", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в on_add_favorite_callback: {e}", exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except Exception as e2:
            logger.error(f"Ошибка при отправке ответа на callback: {e2}", exc_info=True)


async def on_delete_favorite_callback(callback: CallbackQuery):
    """Удаление кабинета из избранного (инлайн-кнопка)."""
    logger.info(f"on_delete_favorite_callback вызван! callback.data = {callback.data}, user_id = {callback.from_user.id if callback.from_user else None}")
    try:
        user_id = callback.from_user.id if callback.from_user else None
        if not user_id:
            logger.warning(f"on_delete_favorite_callback: user_id не найден")
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        data = callback.data or ""
        logger.info(f"on_delete_favorite_callback: обработка callback.data = '{data}', user_id = {user_id}")
        
        # ожидаем формат: del_favorite:ROOM
        if not data.startswith("del_favorite:"):
            logger.warning(f"on_delete_favorite_callback: неверный формат данных: {data}")
            await callback.answer("Неверный формат данных", show_alert=True)
            return
            
        parts = data.split(":", 1)
        room = parts[1].strip() if len(parts) == 2 else ""
        
        if not room:
            logger.warning(f"on_delete_favorite_callback: не удалось извлечь room из {data}")
            await callback.answer("Не удалось определить кабинет", show_alert=True)
            return
        
        logger.info(f"on_delete_favorite_callback: удаление room='{room}' для user_id={user_id}")
        success = remove_favorite(user_id, room)
        if not success:
            logger.error(f"on_delete_favorite_callback: ошибка при удалении room='{room}' для user_id={user_id}")
            await callback.answer("Ошибка при удалении", show_alert=True)
            return
        
        await callback.answer("Удалено", show_alert=False)
        
        # Обновим список в текущем сообщении
        rooms = list_favorites(user_id)
        if rooms:
            kb_rows = [
                [InlineKeyboardButton(text=f"{r} ❌", callback_data=f"del_favorite:{r}")]
                for r in rooms
            ]
            try:
                await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
            except Exception as e:
                logger.error(f"Ошибка при обновлении клавиатуры: {e}", exc_info=True)
        else:
            # если пусто — заменим сообщение
            try:
                await callback.message.edit_text("Избранное пусто.")
            except Exception as e:
                logger.error(f"Ошибка при редактировании сообщения: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Ошибка в on_delete_favorite_callback: {e}", exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except Exception as e2:
            logger.error(f"Ошибка при отправке ответа на callback: {e2}", exc_info=True)


def register_favorites_handlers(dp: Dispatcher):
    """Регистрация обработчиков избранного."""
    # Отладочный обработчик для всех callback queries (регистрируем первым для логирования)
    dp.callback_query.register(debug_callback_handler)
    
    # Избранное: обработчики инлайн добавления/удаления
    dp.message.register(on_favorites_entry, F.text == FAVORITES_ENTRY_TEXT)
    dp.callback_query.register(
        on_add_favorite_callback,
        lambda c: c.data and c.data.startswith("add_favorite:")
    )
    dp.callback_query.register(
        on_delete_favorite_callback,
        lambda c: c.data and c.data.startswith("del_favorite:")
    )
    logger.info("Зарегистрированы обработчики избранного")

