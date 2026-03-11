import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Основные настройки
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
    
    # Google Sheets - ТОЛЬКО URL, без пути к файлу!
    GOOGLE_SHEETS_URL = os.getenv("GOOGLE_SHEETS_URL")
    
    # Информация о салоне
    SALON_NAME = os.getenv("SALON_NAME", "Салон красоты")
    SALON_PHONE = os.getenv("SALON_PHONE")
    SALON_ADDRESS = os.getenv("SALON_ADDRESS")
    SALON_INSTAGRAM = os.getenv("SALON_INSTAGRAM")
    
    # Часы работы
    WORK_HOURS_WEEKDAYS = os.getenv("WORK_HOURS_WEEKDAYS", "10:00-21:00")
    WORK_HOURS_WEEKEND = os.getenv("WORK_HOURS_WEEKEND", "11:00-19:00")
    
    # Настройки времени работы
    WORK_START = int(os.getenv("WORK_START", "10"))
    WORK_END = int(os.getenv("WORK_END", "21"))
    SLOT_DURATION = int(os.getenv("SLOT_DURATION", "30"))
    
    # Настройки напоминаний
    NOTIFICATION_HOURS = int(os.getenv("NOTIFICATION_HOURS", "24"))

config = Config()