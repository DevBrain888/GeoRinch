"""Работа с базой данных избранного"""
import logging
import os
import sqlite3
from typing import List, Optional

logger = logging.getLogger(__name__)

# Путь к базе данных
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "favorites.sqlite3")
_db_conn: Optional[sqlite3.Connection] = None


def get_db() -> sqlite3.Connection:
    """Получить соединение с БД, создав его при необходимости."""
    global _db_conn
    if _db_conn is None:
        try:
            logger.info(f"Инициализация БД избранного: {_DB_PATH}")
            _db_conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
            _db_conn.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER NOT NULL,
                    room TEXT NOT NULL,
                    PRIMARY KEY (user_id, room)
                )
                """
            )
            _db_conn.commit()
            logger.info("Таблица favorites создана/проверена успешно")
        except Exception as e:
            logger.error(f"Ошибка при инициализации БД: {e}", exc_info=True)
            raise
    return _db_conn


def add_favorite(user_id: int, room: str) -> bool:
    """Добавить кабинет в избранное пользователя."""
    try:
        conn = get_db()
        conn.execute(
            "INSERT OR IGNORE INTO favorites(user_id, room) VALUES(?, ?)",
            (user_id, room),
        )
        conn.commit()
        logger.info(f"Добавлено в избранное: user_id={user_id}, room='{room}'")
        return True
    except Exception as e:
        logger.error(f"Ошибка при добавлении в избранное: user_id={user_id}, room='{room}', error={e}", exc_info=True)
        return False


def remove_favorite(user_id: int, room: str) -> bool:
    """Удалить кабинет из избранного пользователя."""
    try:
        conn = get_db()
        cursor = conn.execute("DELETE FROM favorites WHERE user_id = ? AND room = ?", (user_id, room))
        conn.commit()
        deleted_count = cursor.rowcount
        logger.info(f"Удалено из избранного: user_id={user_id}, room='{room}', удалено строк: {deleted_count}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении из избранного: user_id={user_id}, room='{room}', error={e}", exc_info=True)
        return False


def list_favorites(user_id: int) -> List[str]:
    """Получить список избранных кабинетов пользователя."""
    try:
        conn = get_db()
        cur = conn.execute("SELECT room FROM favorites WHERE user_id = ? ORDER BY room", (user_id,))
        rooms = [row[0] for row in cur.fetchall()]
        logger.debug(f"Список избранного для user_id={user_id}: {rooms}")
        return rooms
    except Exception as e:
        logger.error(f"Ошибка при получении списка избранного: user_id={user_id}, error={e}", exc_info=True)
        return []

