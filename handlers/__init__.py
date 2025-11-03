"""Обработчики бота"""
from .errors import register_error_handler
from .start import register_start_handler
from .search import register_search_handlers

__all__ = ['register_error_handler', 'register_start_handler', 'register_search_handlers']

