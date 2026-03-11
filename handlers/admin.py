from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import config
from keyboards.admin import get_admin_keyboard
from database.google_sheets import sheets_manager
from utils.validators import validate_date, validate_time

router = Router()

# Проверка на админа
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Админ-панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    await message.answer(
        "👑 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard()
    )

@router.callback_query(F.data == "admin_today")
async def admin_today(callback: CallbackQuery):
    """Записи на сегодня"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа")
        return
    
    appointments = sheets_manager.get_today_appointments()
    
    if not appointments:
        await callback.message.edit_text(
            "📅 На сегодня записей нет",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()
        return
    
    text = "📅 <b>Записи на сегодня:</b>\n\n"
    for app in appointments:
        text += (
            f"⏰ {app.get('time')}\n"
            f"👤 {app.get('client_name')}\n"
            f"📞 {app.get('client_phone')}\n"
            f"💅 {app.get('service')}\n"
            f"👩 {app.get('master_name')}\n"
            f"{'─' * 20}\n"
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()