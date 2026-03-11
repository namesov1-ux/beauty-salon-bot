#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для очистки и перестройки структуры Google Sheets
Переход на 8 колонок (удаление user_id)
"""

from database.google_sheets import sheets_manager
from datetime import datetime

def cleanup_sheet_8cols():
    """
    Очищает лист schedule и создает новую структуру с 8 колонками
    """
    print("🧹 ОЧИСТКА ТАБЛИЦЫ - ПЕРЕХОД НА 8 КОЛОНОК")
    print("=" * 60)
    
    try:
        # Получаем все значения
        all_values = sheets_manager.schedule_sheet.get_all_values()
        
        if len(all_values) < 2:
            print("❌ В таблице нет данных или только заголовки")
            # Если нет данных, просто создаем правильные заголовки
            sheets_manager.schedule_sheet.clear()
            new_headers = ['date', 'master_id', 'time', 'client_name', 
                          'client_phone', 'service', 'status', 'created_at']
            sheets_manager.schedule_sheet.append_row(new_headers)
            print(f"✅ Созданы новые заголовки: {new_headers}")
            return
        
        print(f"Текущие заголовки: {all_values[0]}")
        print(f"Текущее количество колонок: {len(all_values[0]) if all_values else 0}")
        print(f"Всего строк с данными: {len(all_values) - 1}")
        
        # Новые заголовки (8 колонок)
        new_headers = ['date', 'master_id', 'time', 'client_name', 
                       'client_phone', 'service', 'status', 'created_at']
        
        # Сохраняем данные для переноса
        rows_to_migrate = []
        for i, row in enumerate(all_values[1:], 2):  # Начинаем со 2-й строки
            if len(row) >= 8:
                # Берем только первые 8 колонок
                new_row = row[:8]
                rows_to_migrate.append(new_row)
                print(f"  📄 Строка {i} готова к переносу: {new_row[0]} {new_row[2]} - {new_row[3]}")
            else:
                print(f"  ⚠️ Строка {i} пропущена (мало колонок: {len(row)})")
        
        # Очищаем лист
        sheets_manager.schedule_sheet.clear()
        print("✅ Лист очищен")
        
        # Добавляем новые заголовки
        sheets_manager.schedule_sheet.append_row(new_headers)
        print(f"✅ Добавлены новые заголовки (8 колонок): {new_headers}")
        
        # Добавляем сохраненные данные
        for row in rows_to_migrate:
            sheets_manager.schedule_sheet.append_row(row)
        
        print(f"\n📊 ИТОГ:")
        print(f"   ✅ Перенесено записей: {len(rows_to_migrate)}")
        print(f"   📋 Всего колонок: 8")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка при очистке таблицы: {e}")
        import traceback
        traceback.print_exc()

def verify_sheet_structure():
    """
    Проверка структуры таблицы после очистки
    """
    print("\n🔍 ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ")
    print("=" * 60)
    
    try:
        all_values = sheets_manager.schedule_sheet.get_all_values()
        
        if not all_values:
            print("❌ Таблица пуста")
            return
        
        print(f"Заголовки: {all_values[0]}")
        print(f"Количество колонок: {len(all_values[0])}")
        print(f"Всего строк: {len(all_values)}")
        
        # Проверяем, что нет дубликатов заголовков
        headers = all_values[0]
        if len(headers) != len(set(headers)):
            print("❌ Есть повторяющиеся заголовки!")
            from collections import Counter
            duplicates = [h for h, c in Counter(headers).items() if c > 1]
            print(f"Повторы: {duplicates}")
        else:
            print("✅ Заголовки уникальны")
        
        # Проверяем, что все строки имеют 8 колонок
        for i, row in enumerate(all_values[1:], 2):
            if len(row) != 8:
                print(f"⚠️ Строка {i} имеет {len(row)} колонок (должно быть 8)")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")

if __name__ == "__main__":
    print("🚀 НАЧАЛО ОЧИСТКИ ТАБЛИЦЫ")
    print("=" * 60)
    
    # Запрашиваем подтверждение
    response = input("Это удалит все данные и пересоздаст структуру. Продолжить? (y/n): ")
    
    if response.lower() == 'y':
        cleanup_sheet_8cols()
        verify_sheet_structure()
        print("\n✅ Готово! Теперь можно перезапустить бота.")
    else:
        print("❌ Операция отменена")