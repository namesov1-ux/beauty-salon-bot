from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import config
from keyboards.inline import (
    get_services_keyboard, get_masters_keyboard, get_dates_keyboard,
    get_times_keyboard, get_confirmation_keyboard, get_final_keyboard,
    get_back_keyboard
)
from utils.validators import validate_phone, validate_name, format_phone_for_display
from database.google_sheets import sheets_manager
from states.booking import BookingStates

# СОЗДАЕМ ЭКЗЕМПЛЯР РОУТЕРА
router = Router()

# ==================== ВЫБОР УСЛУГИ ====================

@router.callback_query(F.data == "book")
@router.callback_query(F.data == "back_to_services")
async def select_service(callback: CallbackQuery, state: FSMContext):
    """Выбор услуги"""
    await callback.message.edit_text(
        "✨ <b>Выберите услугу:</b>\n\n"
        "<i>От выбора зависит, какие мастера будут доступны.</i>",
        reply_markup=get_services_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.service_select)
    await callback.answer()

@router.callback_query(BookingStates.service_select, F.data.startswith("service_"))
async def process_service(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора услуги"""
    service = callback.data.replace("service_", "")
    
    # Сохраняем услугу
    await state.update_data(service=service)
    
    # Показываем мастеров
    masters_text = (
        f"👩 <b>К какому мастеру хотите записаться?</b>\n\n"
        f"Услуга: {service}\n\n"
        f"<i>Выберите специалиста:</i>"
    )
    
    await callback.message.edit_text(
        masters_text,
        reply_markup=get_masters_keyboard(service),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.master_select)
    await callback.answer()

# ==================== ВЫБОР МАСТЕРА ====================

@router.callback_query(BookingStates.master_select, F.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    """Назад к выбору услуги"""
    await select_service(callback, state)

@router.callback_query(BookingStates.master_select, F.data.startswith("master_"))
async def process_master(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора мастера"""
    master = callback.data.replace("master_", "")
    
    # Получаем список мастеров из таблицы
    masters_list = sheets_manager.get_masters_list()
    
    # Ищем мастера в списке (без учета регистра)
    found_master = None
    for m in masters_list:
        if m['name'].lower() == master.lower():
            found_master = m['name']  # Используем имя как в таблице
            break
    
    # Если мастер найден, используем его имя, иначе оставляем как есть
    if found_master:
        master = found_master
    
    # Сохраняем мастера
    await state.update_data(master=master)
    
    # Получаем данные для отображения
    data = await state.get_data()
    
    # Показываем выбор даты
    dates_text = (
        f"📅 <b>Выберите удобную дату:</b>\n\n"
        f"Услуга: {data.get('service')}\n"
        f"Мастер: {master}"
    )
    
    await callback.message.edit_text(
        dates_text,
        reply_markup=get_dates_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.date_select)
    await callback.answer()

# ==================== ВЫБОР ДАТЫ ====================

@router.callback_query(BookingStates.date_select, F.data == "back_to_masters")
async def back_to_masters(callback: CallbackQuery, state: FSMContext):
    """Назад к выбору мастера"""
    data = await state.get_data()
    service = data.get('service')
    
    masters_text = (
        f"👩 <b>К какому мастеру хотите записаться?</b>\n\n"
        f"Услуга: {service}\n\n"
        f"<i>Выберите специалиста:</i>"
    )
    
    await callback.message.edit_text(
        masters_text,
        reply_markup=get_masters_keyboard(service),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.master_select)
    await callback.answer()

@router.callback_query(BookingStates.date_select, F.data.startswith("date_"))
async def process_date(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора даты"""
    date = callback.data.replace("date_", "")
    
    # Сохраняем дату
    await state.update_data(date=date)
    
    data = await state.get_data()
    
    # Показываем выбор времени (без упоминания длительности)
    time_text = (
        f"⏰ <b>Выберите удобное время:</b>\n\n"
        f"Дата: {date}"
    )
    
    await callback.message.edit_text(
        time_text,
        reply_markup=get_times_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.time_select)
    await callback.answer()

# ==================== ВЫБОР ВРЕМЕНИ ====================

@router.callback_query(BookingStates.time_select, F.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery, state: FSMContext):
    """Назад к выбору даты"""
    data = await state.get_data()
    
    dates_text = (
        f"📅 <b>Выберите удобную дату:</b>\n\n"
        f"Услуга: {data.get('service')}\n"
        f"Мастер: {data.get('master')}"
    )
    
    await callback.message.edit_text(
        dates_text,
        reply_markup=get_dates_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.date_select)
    await callback.answer()

@router.callback_query(BookingStates.time_select, F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора времени"""
    time = callback.data.replace("time_", "")
    
    data = await state.get_data()
    
    # Проверяем, свободен ли слот
    if not sheets_manager.check_slot_available(data.get('date'), data.get('master'), time):
        await callback.answer(
            "😔 К сожалению, это время уже занято. Выберите другое время.",
            show_alert=True
        )
        return
    
    # Сохраняем время
    await state.update_data(time=time)
    
    # Запрашиваем телефон - ПРОСТО ТЕКСТОМ, БЕЗ КНОПКИ!
    phone_text = (
        "📱 <b>Укажите ваш номер телефона</b>\n\n"
        "Мы отправим напоминание о записи за 24 часа.\n\n"
        "Введите номер в формате: <code>+7XXXXXXXXXX</code> или <code>8XXXXXXXXXX</code>\n\n"
        "<i>Например: +79991234567 или 89991234567</i>"
    )
    
    await callback.message.answer(
        phone_text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.phone_input)
    await callback.answer()

# ==================== ВВОД ТЕЛЕФОНА (ТОЛЬКО ТЕКСТ) ====================

@router.message(BookingStates.phone_input)
async def process_phone_text(message: Message, state: FSMContext):
    """Обработка ввода телефона (только текст, без кнопки)"""
    phone = message.text.strip()
    
    # Валидация телефона
    is_valid, result = validate_phone(phone)
    
    if not is_valid:
        await message.answer(
            f"{result}\n\n"
            "Пожалуйста, введите номер ещё раз в формате:\n"
            "<code>+7XXXXXXXXXX</code> или <code>8XXXXXXXXXX</code>",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем телефон
    await state.update_data(phone=result)
    
    # Запрашиваем имя
    name_text = (
        "👤 <b>Как к вам обращаться?</b>\n\n"
        "Напишите ваше имя в ответном сообщении.\n\n"
        "<i>Например: Анна или Анна Петрова</i>"
    )
    
    await message.answer(
        name_text,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.name_input)

# ==================== ВВОД ИМЕНИ ====================

@router.message(BookingStates.name_input)
async def process_name(message: Message, state: FSMContext):
    """Обработка ввода имени"""
    name = message.text.strip()
    
    # Валидация имени
    is_valid, result = validate_name(name)
    
    if not is_valid:
        await message.answer(
            f"{result}\n\n"
            "Пожалуйста, введите имя ещё раз (только буквы):\n"
            "<i>Например: Анна или Анна Петрова</i>",
            parse_mode="HTML"
        )
        return
    
    # Сохраняем имя
    await state.update_data(name=result)
    
    # Показываем подтверждение
    data = await state.get_data()
    
    confirm_text = (
        f"📝 <b>Проверьте данные записи:</b>\n\n"
        f"👤 Имя: <b>{result}</b>\n"
        f"📞 Телефон: <b>{format_phone_for_display(data.get('phone'))}</b>\n"
        f"💅 Услуга: <b>{data.get('service')}</b>\n"
        f"👩 Мастер: <b>{data.get('master')}</b>\n"
        f"📅 Дата: <b>{data.get('date')}</b>\n"
        f"⏰ Время: <b>{data.get('time')}</b>\n\n"
        f"Всё верно?"
    )
    
    await message.answer(
        confirm_text,
        reply_markup=get_confirmation_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BookingStates.confirmation)

# ==================== ПОДТВЕРЖДЕНИЕ ====================

@router.callback_query(BookingStates.confirmation, F.data == "confirm_yes")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    """Подтверждение записи"""
    
    # Сразу отвечаем на callback, чтобы избежать таймаута
    await callback.answer()
    
    data = await state.get_data()
    
    # ПРОВЕРКА: не сохраняли ли уже эту запись
    if data.get('saved', False):
        await callback.message.edit_text(
            "✅ Запись уже была сохранена ранее!",
            reply_markup=get_final_keyboard()
        )
        return
    
    # Добавляем user_id для напоминаний
    data['user_id'] = callback.from_user.id
    
    # Отправляем уведомление о начале сохранения
    wait_message = await callback.message.edit_text(
        "⏳ Сохраняем вашу запись, пожалуйста подождите..."
    )
    
    # Сохраняем в Google Sheets
    success = sheets_manager.save_appointment(data)
    
    if not success:
        await wait_message.edit_text(
            "❌ Произошла ошибка при сохранении записи. "
            "Пожалуйста, попробуйте позже или свяжитесь с администратором.",
            reply_markup=get_back_keyboard("start")
        )
        return
    
    # Помечаем, что запись сохранена (ЗАЩИТА ОТ ДВОЙНОГО СОХРАНЕНИЯ)
    await state.update_data(saved=True)
    
    # Финальное сообщение
    final_text = (
        f"✅ <b>Вы успешно записаны!</b>\n\n"
        f"✨ Ждём вас <b>{data.get('date')}</b> в <b>{data.get('time')}</b>\n"
        f"👩 Ваш мастер: <b>{data.get('master')}</b>\n\n"
        f"📱 Мы отправим напоминание за 24 часа.\n\n"
        f"Хотите сделать ещё запись?"
    )
    
    await wait_message.edit_text(
        final_text,
        reply_markup=get_final_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(BookingStates.confirmation, F.data == "confirm_no")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    """Отмена записи"""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "❌ Запись отменена. Если хотите начать заново, нажмите /start",
        reply_markup=None
    )

@router.callback_query(F.data == "no_services")
async def no_services(callback: CallbackQuery):
    """Обработка нажатия на кнопку 'нет услуг'"""
    await callback.answer(
        "К сожалению, сейчас нет доступных услуг. Пожалуйста, попробуйте позже.",
        show_alert=True
    )