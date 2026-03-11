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
            
            # Проверяем и создаем заголовки для schedule, если их нет
            if not self.schedule_sheet.get_all_values():
                self.schedule_sheet.append_row([
                    'date', 'master_id', 'time', 'client_name', 
                    'client_phone', 'service', 'status', 'created_at', 'user_id'
                ])
                print("✅ Созданы заголовки для листа schedule")
                
        except Exception as e:
            print(f"Error initializing sheets: {e}")
    
    def get_masters_list(self) -> List[Dict]:
        """
        Получение списка мастеров из листа masters
        """
        try:
            all_records = self.masters_sheet.get_all_records()
            return all_records
        except Exception as e:
            print(f"Error getting masters list: {e}")
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
                    # Разделяем специализации по запятой, если их несколько
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
            # Получаем ID мастера по имени
            master_info = self.get_master_by_name(master)
            if not master_info:
                print(f"Мастер {master} не найден")
                return False
            
            master_id = master_info.get('id')
            
            # Получаем все записи из schedule
            records = self.schedule_sheet.get_all_records()
            
            # Проверяем, нет ли подтвержденной записи на это время
            for record in records:
                if (record.get('date') == date and 
                    record.get('master_id') == master_id and 
                    record.get('time') == time and
                    record.get('status') == 'confirmed'):
                    return False
                
                # Проверяем, не заблокирован ли слот
                if (record.get('date') == date and 
                    record.get('time') == time and
                    record.get('master_id') == master_id and
                    record.get('status') == 'blocked'):
                    return False
            
            # Проверяем блокировку для всех мастеров
            for record in records:
                if (record.get('date') == date and 
                    record.get('time') == time and
                    record.get('master_id') == 0 and
                    record.get('status') == 'blocked'):
                    return False
            
            return True
                
        except Exception as e:
            print(f"Error checking slot: {e}")
            return False
    
    def save_appointment(self, data: dict) -> bool:
        """
        Сохранение записи в таблицу schedule
        """
        try:
            # Получаем ID мастера по имени
            master_info = self.get_master_by_name(data['master'])
            if not master_info:
                print(f"❌ Мастер {data['master']} не найден")
                return False
            
            master_id = master_info.get('id')
            
            # Проверка на дубликаты
            existing_records = self.schedule_sheet.get_all_records()
            for record in existing_records:
                if (record.get('date') == data['date'] and
                    record.get('time') == data['time'] and
                    record.get('master_id') == master_id and
                    record.get('client_name') == data['name']):
                    print(f"⚠️ Дубликат записи, пропускаем")
                    return True
            
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
            
            print(f"✅ Запись сохранена: {data['name']} к мастеру {data['master']}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")
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
            records = self.schedule_sheet.get_all_records()
            masters = self.get_masters_list()
            masters_dict = {m['id']: m['name'] for m in masters}
            
            date_records = []
            for record in records:
                if record.get('date') == date and record.get('status') == 'confirmed':
                    record_copy = dict(record)
                    master_id = record_copy.get('master_id', 0)
                    if master_id == 0:
                        record_copy['master_name'] = 'Все мастера'
                    else:
                        record_copy['master_name'] = masters_dict.get(master_id, f'ID:{master_id}')
                    date_records.append(record_copy)
            
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
                master_id,
                time,
                'ЗАНЯТО',
                '',
                'BLOCKED',
                'blocked',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ''
            ])
            print(f"✅ Слот {date} {time} заблокирован")
            return True
        except Exception as e:
            print(f"❌ Ошибка блокировки слота: {e}")
            return False

# Глобальный экземпляр менеджера
sheets_manager = GoogleSheetsManager()