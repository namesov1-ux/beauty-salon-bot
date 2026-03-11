#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для исправления структуры Google Sheets
Работает напрямую с credentials.json, без переменных окружения
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# ============ НАСТРОЙКИ ============
CREDENTIALS_FILE = "credentials.json"  # файл с ключами
SHEET_URL = "https://docs.google.com/spreadsheets/d/1KsIcPmSYZ8wCGxDr-RBHWdo4XIJaO2_1OZh3lGfL8tU/edit"
# ===================================

def print_header(text):
    """Вывод заголовка"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def check_credentials():
    """Проверяет наличие файла credentials.json"""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Файл {CREDENTIALS_FILE} не найден!")
        print(f"Текущая директория: {os.getcwd()}")
        print("Файлы в директории:")
        for f in os.listdir('.'):
            print(f"  - {f}")
        return False
    print(f"✅ Файл {CREDENTIALS_FILE} найден")
    return True

def connect_to_sheets():
    """Подключение к Google Sheets"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL)
        
        print("✅ Подключение к Google Sheets успешно")
        return sheet
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None

def show_current_structure(sheet):
    """Показывает текущую структуру таблицы"""
    print_header("ТЕКУЩАЯ СТРУКТУРА ТАБЛИЦЫ")
    
    try:
        schedule = sheet.worksheet("schedule")
        all_values = schedule.get_all_values()
        
        if not all_values:
            print("📄 Лист 'schedule' пуст")
            return schedule, []
        
        print(f"📋 Заголовки: {all_values[0]}")
        print(f"📊 Количество колонок: {len(all_values[0])}")
        print(f"📊 Количество строк с данными: {len(all_values) - 1}")
        
        if len(all_values) > 1:
            print("\n📝 Первые 3 строки данных:")
            for i, row in enumerate(all_values[1:4], 1):
                print(f"  {i}. {row}")
        
        return schedule, all_values
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, []

def fix_sheet_structure(schedule, all_values):
    """Исправляет структуру листа schedule"""
    print_header("ИСПРАВЛЕНИЕ СТРУКТУРЫ")
    
    # Новые заголовки (8 колонок, без user_id)
    new_headers = ['date', 'master_id', 'time', 'client_name', 
                   'client_phone', 'service', 'status', 'created_at']
    
    print(f"🆕 Новые заголовки (8 колонок): {new_headers}")
    
    if len(all_values) < 2:
        print("📄 Нет данных для переноса, просто создаем заголовки")
        schedule.clear()
        schedule.append_row(new_headers)
        print("✅ Заголовки созданы")
        return True
    
    # Сохраняем данные для переноса
    rows_to_migrate = []
    skipped = 0
    
    print("\n🔄 Анализ существующих записей:")
    for i, row in enumerate(all_values[1:], 2):
        if len(row) >= 8:
            # Берем только первые 8 колонок
            new_row = row[:8]
            rows_to_migrate.append(new_row)
            print(f"  ✅ Строка {i}: {new_row[0]} {new_row[2]} - {new_row[3]}")
        else:
            skipped += 1
            print(f"  ⚠️ Строка {i} пропущена (только {len(row)} колонок)")
    
    print(f"\n📊 Найдено записей для переноса: {len(rows_to_migrate)}")
    print(f"⚠️ Пропущено записей: {skipped}")
    
    # Запрашиваем подтверждение
    response = input("\nПродолжить очистку и пересоздание структуры? (y/n): ")
    if response.lower() != 'y':
        print("❌ Операция отменена")
        return False
    
    # Очищаем лист
    schedule.clear()
    print("✅ Лист очищен")
    
    # Добавляем новые заголовки
    schedule.append_row(new_headers)
    print("✅ Новые заголовки добавлены")
    
    # Добавляем сохраненные данные
    for row in rows_to_migrate:
        schedule.append_row(row)
    
    print(f"✅ Добавлено {len(rows_to_migrate)} записей")
    return True

def verify_structure(schedule):
    """Проверяет итоговую структуру"""
    print_header("ПРОВЕРКА РЕЗУЛЬТАТА")
    
    all_values = schedule.get_all_values()
    
    if not all_values:
        print("❌ Лист пуст!")
        return False
    
    headers = all_values[0]
    print(f"📋 Итоговые заголовки: {headers}")
    print(f"📊 Количество колонок: {len(headers)}")
    print(f"📊 Всего строк: {len(all_values)}")
    
    # Проверяем, что все строки имеют 8 колонок
    all_good = True
    for i, row in enumerate(all_values[1:], 2):
        if len(row) != 8:
            print(f"⚠️ Строка {i} имеет {len(row)} колонок")
            all_good = False
    
    if all_good and len(headers) == 8:
        print("✅ ВСЁ ОТЛИЧНО! Таблица имеет правильную структуру (8 колонок)")
        return True
    else:
        print("❌ Есть проблемы со структурой")
        return False

def main():
    """Главная функция"""
    print_header("ИСПРАВЛЕНИЕ СТРУКТУРЫ GOOGLE SHEETS")
    
    # Проверяем наличие credentials
    if not check_credentials():
        return
    
    # Подключаемся
    sheet = connect_to_sheets()
    if not sheet:
        return
    
    # Показываем текущую структуру
    schedule, all_values = show_current_structure(sheet)
    if not schedule:
        return
    
    # Исправляем структуру
    if fix_sheet_structure(schedule, all_values):
        # Проверяем результат
        verify_structure(schedule)
        
        print_header("ГОТОВО!")
        print("✅ Таблица успешно исправлена!")
        print("📌 Теперь можно обновить код бота и перезапустить его на Railway")
    else:
        print("❌ Операция не выполнена")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Операция прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()