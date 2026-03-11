import asyncio
import logging
import sys
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from handlers import start, booking, admin, errors
from utils.scheduler import setup_scheduler

# Настройка логирования (убираем лишнее)
logging.basicConfig(
    level=logging.WARNING,  # МЕНЯЕМ НА WARNING, чтобы убрать лишние логи
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Включаем только важные логи
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Отключаем лишние логи от библиотек
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

# Глобальные переменные
bot = None
dp = None
scheduler = None
shutdown_event = asyncio.Event()

# Файл для блокировки
LOCK_FILE = "bot.lock"

def check_single_instance():
    """Быстрая проверка единственного экземпляра"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Для Windows
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(1, False, pid)
                if handle:
                    kernel32.CloseHandle(handle)
                    return False
            else:
                os.kill(pid, 0)
                return False
        except:
            os.remove(LOCK_FILE)
    
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    return True

def cleanup_lock():
    """Удаляет lock-файл"""
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except:
            pass

async def main():
    """Главная функция"""
    global bot, dp, scheduler
    
    # Проверяем единственный экземпляр
    if not check_single_instance():
        logger.error("❌ Бот уже запущен")
        return
    
    # Упрощенная инициализация
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    dp.include_router(errors.router)
    dp.include_router(start.router)
    dp.include_router(booking.router)
    dp.include_router(admin.router)
    
    # Запуск планировщика
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    # Удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Получаем информацию о боте
    me = await bot.get_me()
    logger.info(f"✅ Бот @{me.username} запущен")
    
    # Отправляем уведомление админу
    if config.ADMIN_IDS:
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"✅ Бот запущен\n⏰ {datetime.now().strftime('%H:%M %d.%m')}"
                )
            except:
                pass
    
    try:
        # Запускаем polling с минимальными настройками
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query"],  # Только нужные обновления
            handle_signals=False,
            polling_timeout=30  # Уменьшаем таймаут
        )
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    finally:
        # Очистка
        if scheduler:
            scheduler.shutdown(wait=False)
        if bot:
            await bot.session.close()
        cleanup_lock()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")