import gspread
from google.oauth2.service_account import Credentials
from config import config

def test_connection():
    """Тест подключения к Google Sheets"""
    
    # Настройка доступа
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        # Загружаем credentials
        creds = Credentials.from_service_account_file(
            config.GOOGLE_SHEETS_CREDENTIALS,
            scopes=scope
        )
        
        # Авторизация
        client = gspread.authorize(creds)
        
        # Открываем таблицу
        sheet = client.open_by_url(config.GOOGLE_SHEETS_URL)
        
        # Проверяем доступ к листам
        worksheets = sheet.worksheets()
        print(f"✅ Подключение успешно!")
        print(f"📊 Найдено листов: {len(worksheets)}")
        for ws in worksheets:
            print(f"  - {ws.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    test_connection()