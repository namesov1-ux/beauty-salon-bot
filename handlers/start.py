from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import config
from keyboards.inline import get_start_keyboard, get_back_keyboard
from database.google_sheets import sheets_manager

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()
    
    welcome_text = (
        f"👋 <b>Добро пожаловать в {config.SALON_NAME}!</b>\n\n"
        f"📞 Телефон: {config.SALON_PHONE}\n"
        f"📍 Адрес: {config.SALON_ADDRESS}\n"
        f"📷 Instagram: {config.SALON_INSTAGRAM}\n\n"
        f"🕒 Часы работы:\n"
        f"   Пн-Пт: {config.WORK_HOURS_WEEKDAYS}\n"
        f"   Сб-Вс: {config.WORK_HOURS_WEEKEND}\n\n"
        f"Выберите действие:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.answer()
    
    welcome_text = (
        f"👋 <b>Главное меню</b>\n\n"
        f"Выберите действие:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "masters")
async def show_masters(callback: CallbackQuery):
    """Показать список мастеров"""
    await callback.answer()
    
    masters = sheets_manager.get_masters_list()
    
    if not masters:
        await callback.message.edit_text(
            "❌ Список мастеров временно недоступен",
            reply_markup=get_back_keyboard("main_menu")
        )
        return
    
    text = "👩 <b>Наши мастера:</b>\n\n"
    for master in masters:
        text += (
            f"🔹 <b>{master.get('name')}</b>\n"
            f"   Специализация: {master.get('specialization', 'Не указана')}\n"
            f"   Опыт: {master.get('experience', 'Не указан')}\n\n"
        )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("main_menu"),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "contacts")
async def show_contacts(callback: CallbackQuery):
    """Показать контакты"""
    await callback.answer()
    
    text = (
        f"📞 <b>Контакты</b>\n\n"
        f"🏢 Салон: {config.SALON_NAME}\n"
        f"📍 Адрес: {config.SALON_ADDRESS}\n"
        f"📞 Телефон: {config.SALON_PHONE}\n"
        f"📷 Instagram: {config.SALON_INSTAGRAM}\n\n"
        f"🕒 Часы работы:\n"
        f"   Пн-Пт: {config.WORK_HOURS_WEEKDAYS}\n"
        f"   Сб-Вс: {config.WORK_HOURS_WEEKEND}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("main_menu"),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    """Информация о салоне"""
    await callback.answer()
    
    text = (
        f"ℹ️ <b>О нас</b>\n\n"
        f"{config.SALON_NAME} - это уютный салон красоты в центре города.\n\n"
        f"Мы предлагаем широкий спектр услуг:\n"
        f"• Маникюр и педикюр\n"
        f"• Стрижки и укладки\n"
        f"• Окрашивание волос\n"
        f"• Чистка лица\n"
        f"• Макияж\n"
        f"• Ламинирование ресниц и бровей\n\n"
        f"Работаем с 2015 года. Все мастера имеют профильное образование "
        f"и регулярно повышают квалификацию."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard("main_menu"),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "no_masters")
async def no_masters(callback: CallbackQuery):
    """Обработка нажатия на кнопку 'нет мастеров'"""
    await callback.answer(
        "К сожалению, сейчас нет свободных мастеров для этой услуги",
        show_alert=True
    )