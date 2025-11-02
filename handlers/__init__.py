"""Обработчики бота"""
from .errors import register_error_handler
from .start import register_start_handler

__all__ = ['register_error_handler', 'register_start_handler']

