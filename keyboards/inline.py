from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from database.google_sheets import sheets_manager
from config import config

def get_start_keyboard():
    """Клавиатура для стартового меню"""
    keyboard = [
        [InlineKeyboardButton(text="📅 Записаться", callback_data="book")],
        [InlineKeyboardButton(text="👩 Наши мастера", callback_data="masters")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_services_keyboard():
    """Клавиатура с услугами из специализаций мастеров"""
    keyboard = []
    
    # Получаем список услуг из таблицы
    services = sheets_manager.get_services_list()
    
    if not services:
        # Если услуг нет, показываем заглушку
        keyboard.append([
            InlineKeyboardButton(text="❌ Нет доступных услуг", callback_data="no_services")
        ])
    else:
        # Добавляем услуги из таблицы
        for service in services:
            keyboard.append([
                InlineKeyboardButton(text=f"💅 {service}", callback_data=f"service_{service}")
            ])
    
    # Добавляем кнопку "Назад"
    keyboard.append([
        InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_masters_keyboard(service: str = None):
    """Клавиатура с мастерами из таблицы Google Sheets"""
    keyboard = []
    
    # Получаем список мастеров из таблицы
    if service:
        # Если указана услуга, показываем только мастеров с этой услугой
        masters = sheets_manager.get_masters_by_service(service)
    else:
        # Иначе показываем всех мастеров
        masters = sheets_manager.get_masters_list()
    
    # Добавляем мастеров
    for master in masters:
        name = master.get('name', '')
        specialization = master.get('specialization', '')
        
        # Если есть специализация, показываем её кратко
        spec_short = ""
        if specialization and service:
            # Если выбрана конкретная услуга, показываем её
            spec_short = f" ({service})"
        elif specialization:
            # Иначе показываем первую специализацию
            first_spec = specialization.split(',')[0].strip()
            spec_short = f" ({first_spec})"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"👩 {name}{spec_short}", 
                callback_data=f"master_{name}"
            )
        ])
    
    # Если нет мастеров, показываем сообщение
    if not keyboard:
        keyboard.append([
            InlineKeyboardButton(text="❌ Нет доступных мастеров", callback_data="no_masters")
        ])
    
    # Добавляем кнопку "Назад"
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к услугам", callback_data="back_to_services")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_dates_keyboard():
    """Клавиатура с выбором даты (ближайшие 7 дней)"""
    keyboard = []
    
    # Показываем даты на неделю вперед
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        day_name = get_weekday_name(date.weekday())
        
        # Сегодняшняя дата
        if i == 0:
            button_text = f"📅 Сегодня ({date_str})"
        else:
            button_text = f"📅 {day_name} ({date_str})"
        
        keyboard.append([
            InlineKeyboardButton(text=button_text, callback_data=f"date_{date_str}")
        ])
    
    # Добавляем кнопку "Назад"
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к мастерам", callback_data="back_to_masters")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_times_keyboard():
    """Клавиатура с выбором времени (с 10:00 до 20:00 с шагом 30 минут)"""
    keyboard = []
    row = []
    
    # Генерируем время с 10:00 до 20:00 с шагом 30 минут
    for hour in range(10, 20):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            
            # Добавляем кнопку
            row.append(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))
            
            # Если в ряду 3 кнопки, добавляем ряд в клавиатуру
            if len(row) == 3:
                keyboard.append(row)
                row = []
    
    # Добавляем последний ряд, если он не пустой
    if row:
        keyboard.append(row)
    
    # Добавляем кнопку "Назад"
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к дате", callback_data="back_to_dates")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirmation_keyboard():
    """Клавиатура для подтверждения записи"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Да, всё верно", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Нет, отменить", callback_data="confirm_no")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_final_keyboard():
    """Финальная клавиатура (после записи)"""
    keyboard = [
        [
            InlineKeyboardButton(text="📅 Записаться ещё", callback_data="book"),
            InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard(action: str = "main_menu"):
    """Клавиатура с кнопкой назад"""
    back_text = "🔙 В главное меню" if action == "main_menu" else "🔙 Назад"
    keyboard = [
        [InlineKeyboardButton(text=back_text, callback_data=action)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_weekday_name(weekday: int) -> str:
    """Получение названия дня недели по номеру"""
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return days[weekday]