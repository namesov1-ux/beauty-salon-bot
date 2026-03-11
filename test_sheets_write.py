import asyncio
from database.google_sheets import sheets_manager
from datetime import datetime

async def test_write():
    print("🔍 Тест записи в Google Sheets")
    print("=" * 50)
    
    # Тестовые данные
    test_data = {
        'date': '2026-03-15',
        'time': '15:00',
        'name': 'Тестовый Клиент',
        'phone': '+79991234567',
        'service': 'Маникюр',
        'master': 'Анна',
        'comment': 'Тестовый комментарий'
    }
    
    print(f"📝 Пробуем сохранить: {test_data}")
    
    # Пробуем сохранить
    result = sheets_manager.save_appointment(test_data)
    
    if result:
        print("✅ Успешно сохранено!")
        
        # Проверим, что сохранилось
        today = datetime.now().strftime("%Y-%m-%d")
        records = sheets_manager.get_today_appointments()
        print(f"📊 Записей на сегодня: {len(records)}")
        
    else:
        print("❌ Ошибка при сохранении")

if __name__ == "__main__":
    asyncio.run(test_write())
