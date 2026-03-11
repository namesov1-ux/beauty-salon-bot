import re
from datetime import datetime, timedelta

def validate_phone(phone: str):
    """Быстрая валидация телефона"""
    # Убираем все пробелы и знаки
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Проверяем российские номера
    pattern = r'^((8|\+7)[0-9]{10})$'
    
    if re.match(pattern, phone):
        # Приводим к единому формату
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        return True, phone
    
    return False, "❌ Неверный формат. Используйте: +79991234567 или 89991234567"

def validate_name(name: str):
    """Быстрая валидация имени"""
    name = name.strip()
    
    # Проверяем, что имя не пустое и содержит только буквы
    if not name:
        return False, "❌ Имя не может быть пустым"
    
    if len(name) < 2:
        return False, "❌ Имя слишком короткое"
    
    if len(name) > 50:
        return False, "❌ Имя слишком длинное"
    
    # Разрешаем буквы, пробелы и дефисы
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', name):
        return False, "❌ Имя должно содержать только буквы"
    
    return True, name.title()

def validate_date(date_str: str):
    """Валидация даты"""
    try:
        # Проверяем формат ГГГГ-ММ-ДД
        date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Проверяем, что дата не в прошлом
        if date.date() < datetime.now().date():
            return False, "❌ Дата не может быть в прошлом"
        
        # Проверяем, что дата не слишком далеко (макс 3 месяца)
        if date.date() > (datetime.now() + timedelta(days=90)).date():
            return False, "❌ Можно записаться максимум на 3 месяца вперед"
        
        return True, date_str
    except ValueError:
        return False, "❌ Неверный формат даты"

def validate_time(time_str: str):
    """Валидация времени"""
    try:
        # Проверяем формат ЧЧ:ММ
        time = datetime.strptime(time_str, "%H:%M").time()
        
        # Проверяем рабочее время (можно настроить под ваш салон)
        if time.hour < 9 or time.hour > 21:
            return False, "❌ Время должно быть в рабочее время (9:00-21:00)"
        
        # Проверяем, что время с шагом 30 минут
        if time.minute not in [0, 30]:
            return False, "❌ Время должно быть кратно 30 минутам"
        
        return True, time_str
    except ValueError:
        return False, "❌ Неверный формат времени. Используйте ЧЧ:ММ"

def format_phone_for_display(phone: str):
    """Форматирование телефона для отображения"""
    if phone.startswith('+7') and len(phone) == 12:
        return f"{phone[:2]} ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:12]}"
    return phone