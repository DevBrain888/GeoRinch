"""Обработчики бота"""
from .errors import register_error_handler
from .start import register_start_handler
from .search import register_search_handlers
from .favorites import register_favorites_handlers
from .map import register_map_handlers
from .guide import register_guide_handlers
from .route import register_route_handlers
from .notifications import register_notification_handlers


def register_all_handlers(dp, bot):
    """Регистрация всех обработчиков бота."""
    register_error_handler(dp)
    register_start_handler(dp)
    # ВАЖНО: Порядок регистрации критичен! 
    # Обработчики с фильтрами состояния должны регистрироваться ПЕРВЫМИ
    # чтобы они срабатывали до обработчиков без фильтров
    register_route_handlers(dp)  # Сначала маршрут (имеет фильтры состояния)
    register_map_handlers(dp)    # Затем карта (имеет фильтры состояния)
    register_search_handlers(dp) # Затем поиск (без фильтров, но проверяет состояние внутри)
    register_favorites_handlers(dp)
    register_guide_handlers(dp)
    register_notification_handlers(dp, bot)  # Уведомления (нужен bot для фоновой задачи)


__all__ = [
    'register_error_handler',
    'register_start_handler',
    'register_search_handlers',
    'register_favorites_handlers',
    'register_map_handlers',
    'register_guide_handlers',
    'register_route_handlers',
    'register_all_handlers',
]
