import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import List, Dict
import json
import os
from config import config

class GoogleSheetsManager:
    def __init__(self):
        """Инициализация подключения к Google Sheets"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # ТОЛЬКО переменная окружения, без файла!
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise ValueError("❌ GOOGLE_CREDENTIALS_JSON не найдена в переменных окружения!")
        
        try:
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            print("✅ Загружены credentials из переменной окружения GOOGLE_CREDENTIALS_JSON")
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга GOOGLE_CREDENTIALS_JSON: {e}")
            raise
        except Exception as e:
            print(f"❌ Ошибка создания credentials: {e}")
            raise
        
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_url(config.GOOGLE_SHEETS_URL)
        
        # Получаем существующие листы
        self.masters_sheet = self.sheet.worksheet("masters")
        self.schedule_sheet = self.sheet.worksheet("schedule")
        
        # Инициализируем структуру, если нужно
        self._init_sheets()
        print("✅ Успешное подключение к Google Sheets")
    
    def _init_sheets(self):
        """Инициализация структуры таблицы"""
        try:
            # Проверяем и создаем заголовки для masters, если их нет
            if not self.masters_sheet.get_all_values():
                self.masters_sheet.append_row([
                    'id', 'name', 'specialization', 'experience', 'working_hours'
                ])
                print("✅ Созданы заголовки для листа masters")
            
            # Проверяем и создаем заголовки для schedule, если их нет
            if not self.schedule_sheet.get_all_values():
                self.schedule_sheet.append_row([
                    'date', 'master_id', 'time', 'client_name', 
                    'client_phone', 'service', 'status', 'created_at', 'user_id'
                ])
                print("✅ Созданы заголовки для листа schedule")
                
        except Exception as e:
            print(f"Error initializing sheets: {e}")
    
    # ... остальные методы (get_masters_list, save_appointment и т.д.) остаются без изменений ...
    
    def get_masters_list(self) -> List[Dict]:
        """Получение списка мастеров из листа masters"""
        try:
            all_records = self.masters_sheet.get_all_records()
            return all_records
        except Exception as e:
            print(f"Error getting masters list: {e}")
            return []
    
    def save_appointment(self, data: dict) -> bool:
        """Сохранение записи в таблицу schedule"""
        try:
            # Получаем ID мастера по имени
            master_info = self.get_master_by_name(data['master'])
            if not master_info:
                print(f"❌ Мастер {data['master']} не найден в таблице")
                return False
            
            master_id = master_info.get('id')
            
            # Сохраняем запись
            self.schedule_sheet.append_row([
                data['date'],
                master_id,
                data['time'],
                data['name'],
                data['phone'],
                data['service'],
                'confirmed',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get('user_id', '')
            ])
            
            print(f"✅ Запись сохранена: {data['name']} к мастеру {data['master']} на {data['date']} {data['time']}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
            return False
    
    def get_master_by_name(self, name: str) -> Dict:
        """Получение мастера по имени"""
        try:
            masters = self.get_masters_list()
            for master in masters:
                if master.get('name', '').lower() == name.lower():
                    return master
            return {}
        except Exception as e:
            print(f"Error getting master by name: {e}")
            return {}

# Глобальный экземпляр менеджера
sheets_manager = GoogleSheetsManager()