from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    """Состояния процесса записи"""
    welcome = State()              # Приветствие
    service_select = State()       # Выбор услуги
    master_select = State()        # Выбор мастера
    date_select = State()          # Выбор даты
    time_select = State()          # Выбор времени
    phone_input = State()          # Ввод телефона
    name_input = State()           # Ввод имени
    confirmation = State()         # Подтверждение

class AdminStates(StatesGroup):
    """Состояния для администратора"""
    block_date = State()           # Блокировка даты
    block_time = State()           # Блокировка времени
    manual_name = State()          # Ручная запись - имя
    manual_phone = State()         # Ручная запись - телефон
    manual_service = State()       # Ручная запись - услуга
    manual_master = State()        # Ручная запись - мастер
    manual_date = State()          # Ручная запись - дата
    manual_time = State()          # Ручная запись - время