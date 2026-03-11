from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from aiogram import Bot
import logging

from database.google_sheets import sheets_manager
from utils.validators import format_phone_for_display

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def send_reminder(bot: Bot, user_id: int, appointment_data: dict):
    """Отправка напоминания о записи"""
    try:
        reminder_text = (
            f"🔔 <b>Напоминание о записи</b>\n\n"
            f"⏰ Завтра в <b>{appointment_data['time']}</b>\n"
            f"👩 Мастер: <b>{appointment_data['master_name']}</b>\n"
            f"💅 Услуга: <b>{appointment_data['service']}</b>\n\n"
            f"Если планы изменились, пожалуйста, отмените запись:\n"
            f"📞 {appointment_data['salon_phone']}"
        )
        
        await bot.send_message(user_id, reminder_text)
        logger.info(f"Reminder sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending reminder: {e}")

def setup_scheduler(bot: Bot):
    """Настройка планировщика задач"""
    
    async def check_and_schedule_reminders():
        """Проверка записей и планирование напоминаний"""
        try:
            # Получаем все записи
            # В реальном проекте нужно получать записи на завтра
            appointments = sheets_manager.get_today_appointments()  # Замените на get_tomorrow
            
            for apt in appointments:
                # Парсим дату и время записи
                appointment_dt = datetime.strptime(
                    f"{apt['date']} {apt['time']}", 
                    "%Y-%m-%d %H:%M"
                )
                
                # Отправляем за 24 часа
                reminder_time = appointment_dt - timedelta(hours=24)
                
                # Если время напоминания в будущем
                if reminder_time > datetime.now():
                    scheduler.add_job(
                        send_reminder,
                        trigger=DateTrigger(run_date=reminder_time),
                        args=[bot, apt.get('user_id'), apt],
                        id=f"reminder_{apt['date']}_{apt['time']}_{apt.get('user_id')}",
                        replace_existing=True
                    )
                    logger.info(f"Scheduled reminder for {apt['date']} {apt['time']}")
                    
        except Exception as e:
            logger.error(f"Error in reminder scheduler: {e}")
    
    # Проверяем каждые 6 часов
    scheduler.add_job(
        check_and_schedule_reminders,
        trigger='interval',
        hours=6,
        id='check_reminders',
        replace_existing=True
    )
    
    # Первоначальная проверка при запуске
    scheduler.add_job(
        check_and_schedule_reminders,
        trigger='date',
        run_date=datetime.now(),
        id='initial_reminder_check'
    )
    
    return scheduler