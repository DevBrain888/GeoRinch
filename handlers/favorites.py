"""Обработчики для функционала избранного"""
import logging
from aiogram import Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from keyboards import get_main_keyboard
from handlers.constants import (
    FAVORITES_ENTRY_TEXT,
    FIRST_FLOOR_ROOM_BUTTONS,
    SECOND_FLOOR_ROOM_BUTTONS,
    THIRD_FLOOR_ROOM_BUTTONS,
    FOURTH_FLOOR_ROOM_BUTTONS,
    FIRST_FLOOR_ROOM_IMAGE_URL,
    SECOND_FLOOR_ROOM_IMAGE_URL,
    THIRD_FLOOR_ROOM_IMAGE_URL,
    FOURTH_FLOOR_ROOM_IMAGE_URL,
    FIRST_FLOOR_SELECTED_ROOM_101,
    FIRST_FLOOR_SELECTED_ROOM_102,
    FIRST_FLOOR_SELECTED_ROOM_103,
    FIRST_FLOOR_SELECTED_ROOM_104,
    FIRST_FLOOR_SELECTED_ROOM_105,
    FIRST_FLOOR_SELECTED_ROOM_106,
    FIRST_FLOOR_SELECTED_ROOM_107,
    FIRST_FLOOR_SELECTED_ROOM_108,
    FIRST_FLOOR_SELECTED_ROOM_109,
    FIRST_FLOOR_SELECTED_ROOM_110,
    FIRST_FLOOR_SELECTED_ROOM_111,
    FIRST_FLOOR_SELECTED_ROOM_Охрана,
    FIRST_FLOOR_SELECTED_ROOM_Гардероб,
    FIRST_FLOOR_SELECTED_ROOM_Туалет,
)
from handlers.db.favorites import add_favorite, remove_favorite, list_favorites
from handlers.notifications import add_user_to_main_menu, remove_user_from_main_menu

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
        remove_user_from_main_menu(user_id)  # Удаляем из главного меню при входе в избранное
        rooms = list_favorites(user_id)
        if not rooms:
            await message.answer("Избранное пусто.", reply_markup=get_main_keyboard())
            # Отслеживаем, что пользователь вернулся в главное меню
            add_user_to_main_menu(user_id)
            return
        kb_rows = []
        for room in rooms:
            kb_rows.append([
                InlineKeyboardButton(text=f"{room} 🔎", callback_data=f"show_favorite:{room}"),
                InlineKeyboardButton(text=f"{room} ❌", callback_data=f"del_favorite:{room}")
            ])
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
            kb_rows = []
            for r in rooms:
                kb_rows.append([
                    InlineKeyboardButton(text=f"{r} 🔎", callback_data=f"show_favorite:{r}"),
                    InlineKeyboardButton(text=f"{r} ❌", callback_data=f"del_favorite:{r}")
                ])
            try:
                await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
            except Exception as e:
                logger.error(f"Ошибка при обновлении клавиатуры: {e}", exc_info=True)
        else:
            # если пусто — заменим сообщение
            try:
                await callback.message.edit_text("Избранное пусто.")
                # Отслеживаем, что пользователь вернулся в главное меню
                add_user_to_main_menu(user_id)
            except Exception as e:
                logger.error(f"Ошибка при редактировании сообщения: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Ошибка в on_delete_favorite_callback: {e}", exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except Exception as e2:
            logger.error(f"Ошибка при отправке ответа на callback: {e2}", exc_info=True)


async def on_show_favorite_callback(callback: CallbackQuery):
    """Показать кабинет из избранного (инлайн-кнопка)."""
    logger.info(f"on_show_favorite_callback вызван! callback.data = {callback.data}, user_id = {callback.from_user.id if callback.from_user else None}")
    try:
        user_id = callback.from_user.id if callback.from_user else None
        if not user_id:
            logger.warning(f"on_show_favorite_callback: user_id не найден")
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return

        data = callback.data or ""
        if not data.startswith("show_favorite:"):
            logger.warning(f"on_show_favorite_callback: неверный формат данных: {data}")
            await callback.answer("Неверный формат данных", show_alert=True)
            return

        parts = data.split(":", 1)
        room = parts[1].strip() if len(parts) == 2 else ""
        if not room:
            logger.warning(f"on_show_favorite_callback: не удалось извлечь room из {data}")
            await callback.answer("Не удалось определить кабинет", show_alert=True)
            return

        # Словарь для сопоставления кабинетов первого этажа с их изображениями
        FIRST_FLOOR_ROOM_IMAGES = {
            "101": FIRST_FLOOR_SELECTED_ROOM_101,
            "102": FIRST_FLOOR_SELECTED_ROOM_102,
            "103": FIRST_FLOOR_SELECTED_ROOM_103,
            "104": FIRST_FLOOR_SELECTED_ROOM_104,
            "105": FIRST_FLOOR_SELECTED_ROOM_105,
            "106": FIRST_FLOOR_SELECTED_ROOM_106,
            "107": FIRST_FLOOR_SELECTED_ROOM_107,
            "108": FIRST_FLOOR_SELECTED_ROOM_108,
            "109": FIRST_FLOOR_SELECTED_ROOM_109,
            "110": FIRST_FLOOR_SELECTED_ROOM_110,
            "111": FIRST_FLOOR_SELECTED_ROOM_111,
            "Охрана": FIRST_FLOOR_SELECTED_ROOM_Охрана,
            "Гардероб": FIRST_FLOOR_SELECTED_ROOM_Гардероб,
            "Туалет": FIRST_FLOOR_SELECTED_ROOM_Туалет,
        }
        
        # Определяем этаж по названию кабинета
        if room in FIRST_FLOOR_ROOM_BUTTONS:
            # Для первого этажа проверяем, есть ли специальное изображение
            if room in FIRST_FLOOR_ROOM_IMAGES:
                image_url = FIRST_FLOOR_ROOM_IMAGES[room]
            else:
                # Если нет специального изображения, используем общее изображение этажа
                image_url = FIRST_FLOOR_ROOM_IMAGE_URL
        elif room in SECOND_FLOOR_ROOM_BUTTONS:
            image_url = SECOND_FLOOR_ROOM_IMAGE_URL
        elif room in THIRD_FLOOR_ROOM_BUTTONS:
            image_url = THIRD_FLOOR_ROOM_IMAGE_URL
        elif room in FOURTH_FLOOR_ROOM_BUTTONS:
            image_url = FOURTH_FLOOR_ROOM_IMAGE_URL
        else:
            # Если кабинет не распознан, показываем первый этаж по умолчанию
            image_url = FIRST_FLOOR_ROOM_IMAGE_URL

        await callback.answer()
        await callback.message.answer_photo(photo=image_url, caption=f"Кабинет: {room}")
    except Exception as e:
        logger.error(f"Ошибка в on_show_favorite_callback: {e}", exc_info=True)
        try:
            await callback.answer("Произошла ошибка", show_alert=True)
        except Exception as e2:
            logger.error(f"Ошибка при отправке ответа на callback: {e2}", exc_info=True)


def register_favorites_handlers(dp: Dispatcher):
    """Регистрация обработчиков избранного."""
    # Избранное: обработчики инлайн добавления/удаления
    dp.message.register(on_favorites_entry, F.text == FAVORITES_ENTRY_TEXT)
    dp.callback_query.register(
        on_add_favorite_callback,
        lambda c: c.data and c.data.startswith("add_favorite:")
    )
    dp.callback_query.register(
        on_show_favorite_callback,
        lambda c: c.data and c.data.startswith("show_favorite:")
    )
    dp.callback_query.register(
        on_delete_favorite_callback,
        lambda c: c.data and c.data.startswith("del_favorite:")
    )
    logger.info("Зарегистрированы обработчики избранного")

