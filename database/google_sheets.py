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
        
        # Загрузка credentials из переменной окружения
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise ValueError("❌ GOOGLE_CREDENTIALS_JSON не найдена в переменных окружения!")
        
        try:
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            print("✅ Загружены credentials из переменной окружения GOOGLE_CREDENTIALS_JSON")
        except Exception as e:
            print(f"❌ Ошибка загрузки credentials: {e}")
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
            
            # Проверяем и создаем заголовки для schedule (8 колонок, без user_id)
            if not self.schedule_sheet.get_all_values():
                self.schedule_sheet.append_row([
                    'date', 'master_id', 'time', 'client_name', 
                    'client_phone', 'service', 'status', 'created_at'
                ])
                print("✅ Созданы заголовки для листа schedule (8 колонок)")
                
        except Exception as e:
            print(f"Error initializing sheets: {e}")
    
    def get_masters_list(self) -> List[Dict]:
        """
        Получение списка мастеров из листа masters
        """
        try:
            all_values = self.masters_sheet.get_all_values()
            
            if len(all_values) < 2:
                return []
            
            headers = all_values[0]
            masters = []
            for row in all_values[1:]:
                if len(row) >= len(headers):
                    master = {}
                    for i, header in enumerate(headers):
                        if header:
                            master[header] = row[i] if i < len(row) else ''
                    masters.append(master)
            
            return masters
            
        except Exception as e:
            print(f"Error getting masters list: {e}")
            return []
    
    def get_schedule_records(self) -> List[Dict]:
        """
        Получение записей из schedule (8 колонок, без user_id)
        """
        try:
            all_values = self.schedule_sheet.get_all_values()
            
            if len(all_values) < 2:
                return []
            
            records = []
            for row in all_values[1:]:
                if len(row) >= 8:
                    record = {
                        'date': row[0] if len(row) > 0 else '',
                        'master_id': row[1] if len(row) > 1 else '',
                        'time': row[2] if len(row) > 2 else '',
                        'client_name': row[3] if len(row) > 3 else '',
                        'client_phone': row[4] if len(row) > 4 else '',
                        'service': row[5] if len(row) > 5 else '',
                        'status': row[6] if len(row) > 6 else '',
                        'created_at': row[7] if len(row) > 7 else ''
                    }
                    records.append(record)
            
            return records
            
        except Exception as e:
            print(f"Error getting schedule records: {e}")
            return []
    
    def get_services_list(self) -> List[str]:
        """
        Получение списка уникальных услуг из специализаций мастеров
        """
        try:
            masters = self.get_masters_list()
            services = set()
            
            for master in masters:
                specialization = master.get('specialization', '')
                if specialization:
                    for service in specialization.split(','):
                        service = service.strip()
                        if service:
                            services.add(service)
            
            return sorted(list(services))
        except Exception as e:
            print(f"Error getting services list: {e}")
            return []
    
    def get_masters_by_service(self, service: str) -> List[Dict]:
        """
        Получение списка мастеров, предоставляющих конкретную услугу
        """
        try:
            masters = self.get_masters_list()
            result = []
            
            for master in masters:
                specialization = master.get('specialization', '')
                if service.lower() in specialization.lower():
                    result.append(master)
            
            return result
        except Exception as e:
            print(f"Error getting masters by service: {e}")
            return []
    
    def get_master_by_name(self, name: str) -> Dict:
        """
        Получение мастера по имени
        """
        try:
            masters = self.get_masters_list()
            for master in masters:
                if master.get('name', '').lower() == name.lower():
                    return master
            return {}
        except Exception as e:
            print(f"Error getting master by name: {e}")
            return {}
    
    def check_slot_available(self, date: str, master: str, time: str) -> bool:
        """
        Проверка, свободен ли слот
        """
        try:
            master_info = self.get_master_by_name(master)
            if not master_info:
                print(f"❌ Мастер {master} не найден")
                return False
            
            master_id = master_info.get('id')
            print(f"🔍 Проверка слота: {date} {time} для мастера {master} (ID: {master_id})")
            
            records = self.get_schedule_records()
            
            for record in records:
                if (record.get('date') == date and 
                    record.get('master_id') == str(master_id) and 
                    record.get('time') == time):
                    
                    if record.get('status') in ['confirmed', 'blocked']:
                        print(f"⛔ Слот {date} {time} занят")
                        return False
                
                if (record.get('date') == date and 
                    record.get('time') == time and
                    record.get('master_id') == '0' and
                    record.get('status') == 'blocked'):
                    print(f"⛔ Слот {date} {time} заблокирован для всех")
                    return False
            
            print(f"✅ Слот {date} {time} свободен")
            return True
                
        except Exception as e:
            print(f"❌ Ошибка в check_slot_available: {e}")
            return False
    
    def save_appointment(self, data: dict) -> bool:
        """
        Сохранение записи в таблицу schedule (без user_id)
        """
        try:
            # Получаем информацию о мастере по имени
            master_info = self.get_master_by_name(data['master'])
            if not master_info:
                print(f"❌ Мастер {data['master']} не найден в таблице")
                return False
            
            master_id = master_info.get('id')
            print(f"📋 Мастер найден: {data['master']} (ID: {master_id})")
            
            # Проверка на дубликаты
            existing_records = self.get_schedule_records()
            
            for record in existing_records:
                if (record.get('date') == data['date'] and
                    record.get('time') == data['time'] and
                    record.get('master_id') == str(master_id) and
                    record.get('client_name') == data['name']):
                    
                    print(f"⚠️ Обнаружен дубликат записи, пропускаем")
                    return True
            
            # Сохраняем запись - ТОЛЬКО 8 КОЛОНОК, БЕЗ user_id!
            row_data = [
                data['date'],                          # 1. date
                str(master_id),                         # 2. master_id
                data['time'],                           # 3. time
                data['name'],                           # 4. client_name
                data['phone'],                          # 5. client_phone
                data['service'],                         # 6. service
                'confirmed',                             # 7. status
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 8. created_at
            ]
            
            print(f"📝 Сохраняем строку из {len(row_data)} колонок: {row_data}")
            self.schedule_sheet.append_row(row_data)
            
            print(f"✅ Запись успешно сохранена: {data['name']} к мастеру {data['master']} на {data['date']} {data['time']}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении записи: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_today_appointments(self) -> List[Dict]:
        """
        Получение записей на сегодня
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return self.get_appointments_by_date(today)
        except Exception as e:
            print(f"Error getting today appointments: {e}")
            return []
    
    def get_appointments_by_date(self, date: str) -> List[Dict]:
        """
        Получение записей на конкретную дату
        """
        try:
            records = self.get_schedule_records()
            masters = self.get_masters_list()
            masters_dict = {str(m['id']): m['name'] for m in masters if 'id' in m}
            
            date_records = []
            for record in records:
                if record.get('date') == date and record.get('status') == 'confirmed':
                    record['master_name'] = masters_dict.get(
                        record.get('master_id', '0'), 
                        f"ID:{record.get('master_id')}"
                    )
                    date_records.append(record)
            
            date_records.sort(key=lambda x: x.get('time', ''))
            return date_records
        except Exception as e:
            print(f"Error getting appointments by date: {e}")
            return []
    
    def block_slot(self, date: str, time: str, master_id: int = 0) -> bool:
        """
        Блокировка слота
        """
        try:
            self.schedule_sheet.append_row([
                date,
                str(master_id),
                time,
                'ЗАНЯТО',
                '',
                'BLOCKED',
                'blocked',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            print(f"✅ Слот {date} {time} заблокирован")
            return True
        except Exception as e:
            print(f"❌ Ошибка блокировки слота: {e}")
            return False

# Глобальный экземпляр менеджера
sheets_manager = GoogleSheetsManager()