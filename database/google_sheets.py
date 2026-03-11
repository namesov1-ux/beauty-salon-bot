import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from typing import List, Dict
import json
import os
from config import config

class GoogleSheetsManager:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Пробуем загрузить из переменной окружения
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if creds_json:
            creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scope)
            print("✅ Загружены credentials из переменной окружения")
        else:
            creds = Credentials.from_service_account_file(config.GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
            print(f"✅ Загружены credentials из файла: {config.GOOGLE_SHEETS_CREDENTIALS}")
        
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_url(config.GOOGLE_SHEETS_URL)
        self.masters_sheet = self.sheet.worksheet("masters")
        self.schedule_sheet = self.sheet.worksheet("schedule")
        print("✅ Подключение к Google Sheets установлено")
    
    # ... остальные методы остаются без изменений ...

sheets_manager = GoogleSheetsManager()
