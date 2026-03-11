import logging
from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramNetworkError
)

router = Router()
logger = logging.getLogger(__name__)

@router.error()
async def error_handler(event: ErrorEvent):
    """Быстрый обработчик ошибок"""
    
    # Игнорируем частые неопасные ошибки
    if isinstance(event.exception, TelegramBadRequest):
        if any(msg in str(event.exception).lower() for msg in [
            "message is not modified",
            "query is too old"
        ]):
            return  # Просто игнорируем
    
    # Логируем только важные ошибки
    logger.error(f"Ошибка: {event.exception}")