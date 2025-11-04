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
from pathfinder import get_path_image
from aiogram.types import BufferedInputFile

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
            # Проверяем, является ли это маршрутом
            if room.startswith("route:"):
                # Формат: route:room_a:room_b
                parts = room.split(":", 2)
                if len(parts) == 3:
                    room_a, room_b = parts[1], parts[2]
                    display_text = f"{room_a} → {room_b} 🔎"
                else:
                    display_text = f"{room} 🔎"
            else:
                display_text = f"{room} 🔎"
            # Определяем текст для кнопки удаления
            if room.startswith("route:"):
                parts = room.split(":", 2)
                if len(parts) == 3:
                    delete_text = f"{parts[2]} ❌"
                else:
                    delete_text = f"{room} ❌"
            else:
                delete_text = f"{room} ❌"
            
            kb_rows.append([
                InlineKeyboardButton(text=display_text, callback_data=f"show_favorite:{room}"),
                InlineKeyboardButton(text=delete_text, callback_data=f"del_favorite:{room}")
            ])
        inline_kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
        await message.answer("Ваши избраные кабинеты и маршруты", reply_markup=inline_kb)
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
                # Проверяем, является ли это маршрутом
                if r.startswith("route:"):
                    parts = r.split(":", 2)
                    if len(parts) == 3:
                        room_a, room_b = parts[1], parts[2]
                        display_text = f"{room_a} → {room_b} 🔎"
                        delete_text = f"{room_b} ❌"
                    else:
                        display_text = f"{r} 🔎"
                        delete_text = f"{r} ❌"
                else:
                    display_text = f"{r} 🔎"
                    delete_text = f"{r} ❌"
                kb_rows.append([
                    InlineKeyboardButton(text=display_text, callback_data=f"show_favorite:{r}"),
                    InlineKeyboardButton(text=delete_text, callback_data=f"del_favorite:{r}")
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


async def on_add_route_favorite_callback(callback: CallbackQuery):
    """Добавление маршрута в избранное (инлайн-кнопка)."""
    logger.info(f"on_add_route_favorite_callback вызван! callback.data = {callback.data}, user_id = {callback.from_user.id if callback.from_user else None}")
    try:
        user_id = callback.from_user.id if callback.from_user else None
        if not user_id:
            logger.warning(f"on_add_route_favorite_callback: user_id не найден")
            await callback.answer("Ошибка: пользователь не найден", show_alert=True)
            return
        
        data = callback.data or ""
        logger.info(f"on_add_route_favorite_callback: обработка callback.data = '{data}', user_id = {user_id}")
        
        # ожидаем формат: add_route_favorite:route:room_a:room_b
        if not data.startswith("add_route_favorite:"):
            logger.warning(f"on_add_route_favorite_callback: неверный формат данных: {data}")
            await callback.answer("Неверный формат данных", show_alert=True)
            return
            
        parts = data.split(":", 1)
        route_key = parts[1].strip() if len(parts) == 2 else ""
        
        if not route_key or not route_key.startswith("route:"):
            logger.warning(f"on_add_route_favorite_callback: не удалось извлечь route_key из {data}")
            await callback.answer("Не удалось определить маршрут", show_alert=True)
            return
        
        logger.info(f"on_add_route_favorite_callback: добавление route='{route_key}' для user_id={user_id}")
        success = add_favorite(user_id, route_key)
        if success:
            logger.info(f"on_add_route_favorite_callback: успешно добавлено route='{route_key}' для user_id={user_id}")
            await callback.answer("Маршрут добавлен в избранное", show_alert=False)
            # Возвращаем пользователя в главное меню
            add_user_to_main_menu(user_id)
            await callback.message.answer("Маршрут сохранен в избранное! Вы можете найти его в разделе 'Избранное'.", reply_markup=get_main_keyboard())
        else:
            logger.error(f"on_add_route_favorite_callback: ошибка при добавлении route='{route_key}' для user_id={user_id}")
            await callback.answer("Ошибка при добавлении", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в on_add_route_favorite_callback: {e}", exc_info=True)
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

        # Проверяем, является ли это маршрутом
        if room.startswith("route:"):
            # Формат: route:room_a:room_b
            route_parts = room.split(":", 2)
            if len(route_parts) != 3:
                logger.warning(f"on_show_favorite_callback: неверный формат маршрута: {room}")
                await callback.answer("Неверный формат маршрута", show_alert=True)
                return
            
            room_a, room_b = route_parts[1], route_parts[2]
            
            # Определяем этаж по первому кабинету
            floor = 1  # По умолчанию первый этаж
            if room_a in FIRST_FLOOR_ROOM_BUTTONS:
                floor = 1
            elif room_a in SECOND_FLOOR_ROOM_BUTTONS:
                floor = 2
            elif room_a in THIRD_FLOOR_ROOM_BUTTONS:
                floor = 3
            elif room_a in FOURTH_FLOOR_ROOM_BUTTONS:
                floor = 4
            
            # Проверяем, что маршрут только для первого этажа
            if floor != 1:
                await callback.answer("Маршрут для этого этажа пока не поддерживается", show_alert=True)
                return
            
            # Строим путь
            try:
                path_image = get_path_image(room_a, room_b, floor)
                if path_image is None:
                    await callback.answer("Не удалось построить маршрут", show_alert=True)
                    return
                
                path_image.seek(0)
                photo_file = BufferedInputFile(
                    path_image.read(),
                    filename="route.png"
                )
                await callback.answer()
                # Возвращаем пользователя в главное меню
                add_user_to_main_menu(user_id)
                await callback.message.answer_photo(
                    photo=photo_file,
                    caption=f"Маршрут от кабинета {room_a} до кабинета {room_b}",
                    reply_markup=get_main_keyboard()
                )
            except Exception as e:
                logger.error(f"Ошибка при построении маршрута из избранного: {e}", exc_info=True)
                await callback.answer("Ошибка при построении маршрута", show_alert=True)
            return

        # Если это обычный кабинет, обрабатываем как раньше
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
        on_add_route_favorite_callback,
        lambda c: c.data and c.data.startswith("add_route_favorite:")
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

