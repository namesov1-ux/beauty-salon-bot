import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError

logger = logging.getLogger(__name__)

class ConnectionMonitor:
    """Мониторинг соединения с Telegram API"""
    
    def __init__(self, bot: Bot, check_interval: int = 60):
        self.bot = bot
        self.check_interval = check_interval
        self.is_connected = True
        self._monitor_task = None
        self._connection_lost_time = None
    
    async def start_monitoring(self):
        """Запуск мониторинга соединения"""
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("✅ Мониторинг соединения запущен")
    
    async def stop_monitoring(self):
        """Остановка мониторинга"""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Мониторинг соединения остановлен")
    
    async def _monitor_loop(self):
        """Цикл мониторинга"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                
                # Проверяем соединение, получая информацию о боте
                me = await self.bot.get_me()
                
                if not self.is_connected:
                    # Восстановление соединения
                    downtime = asyncio.get_event_loop().time() - self._connection_lost_time
                    logger.info(f"✅ Соединение восстановлено после {downtime:.1f} сек простоя")
                    self.is_connected = True
                    self._connection_lost_time = None
                    
            except TelegramNetworkError as e:
                if self.is_connected:
                    logger.warning(f"⚠️ Потеря соединения с Telegram API: {e}")
                    self.is_connected = False
                    self._connection_lost_time = asyncio.get_event_loop().time()
                    
            except asyncio.CancelledError:
                break
                
            except Exception as e:
                logger.error(f"❌ Ошибка в мониторинге соединения: {e}")