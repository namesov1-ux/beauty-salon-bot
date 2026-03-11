import asyncio
import logging
import psutil
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class BotMonitor:
    """Мониторинг состояния бота"""
    
    def __init__(self, bot, check_interval: int = 60):
        self.bot = bot
        self.check_interval = check_interval
        self._monitor_task = None
        self.start_time = datetime.now()
        self.update_count = 0
        self.error_count = 0
    
    async def start(self):
        """Запуск мониторинга"""
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("✅ Мониторинг запущен")
    
    async def stop(self):
        """Остановка мониторинга"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Мониторинг остановлен")
    
    async def _monitor_loop(self):
        """Цикл мониторинга"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                
                # Получаем информацию о процессе
                process = psutil.Process(os.getpid())
                memory_usage = process.memory_info().rss / 1024 / 1024  # в MB
                cpu_usage = process.cpu_percent()
                
                # Время работы
                uptime = datetime.now() - self.start_time
                
                logger.info("📊 Статистика бота:")
                logger.info(f"   ⏱️  Время работы: {uptime}")
                logger.info(f"   💾 Память: {memory_usage:.2f} MB")
                logger.info(f"   🔧 CPU: {cpu_usage:.1f}%")
                logger.info(f"   📨 Обработано обновлений: {self.update_count}")
                logger.info(f"   ❌ Ошибок: {self.error_count}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Ошибка мониторинга: {e}")
    
    def increment_updates(self):
        """Увеличить счетчик обновлений"""
        self.update_count += 1
    
    def increment_errors(self):
        """Увеличить счетчик ошибок"""
        self.error_count += 1