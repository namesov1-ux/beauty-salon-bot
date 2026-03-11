# 💅 Beauty Salon Bot

Telegram бот для записи в салон красоты. Интеграция с Google Sheets для хранения данных о мастерах и записях.

## ✨ Возможности

- 📅 Запись на услуги через удобное меню
- 👩 Выбор мастера по специализации
- 📱 Сбор контактных данных клиентов
- 🔒 Блокировка слотов администратором
- 📊 Просмотр записей на дату
- 📈 Статистика записей

## 🛠 Технологии

- Python 3.11
- Aiogram 3.x
- Google Sheets API
- APScheduler
- Railway (хостинг)

## 📦 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/beauty-salon-bot.git
cd beauty-salon-bot
Создайте виртуальное окружение:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Установите зависимости:

bash
pip install -r requirements.txt
Создайте файл .env из примера:

bash
cp .env.example .env
Отредактируйте .env файл с вашими данными:

BOT_TOKEN - токен от @BotFather

ADMIN_IDS - ваш Telegram ID

GOOGLE_SHEETS_URL - ссылка на вашу таблицу

Добавьте credentials.json (файл сервисного аккаунта Google)

🚀 Запуск
bash
python main.py
☁️ Деплой на Railway
Запушьте код на GitHub

Подключите репозиторий к Railway

Добавьте переменные окружения в Railway (все из .env)

Загрузите credentials.json через вкладку Files

Railway автоматически развернет бота

📊 Google Sheets структура
Лист "masters" (мастера)
id	name	specialization	experience	working_hours
1	Анна	Маникюр,Педикюр	5 лет	10:00-20:00
2	Елена	Стрижка,Окрашивание	7 лет	10:00-20:00
Лист "schedule" (расписание)
date	master_id	time	client_name	client_phone	service	status	created_at	user_id
2026-03-15	1	15:00	Анна Петрова	+79991234567	Маникюр	confirmed	2026-03-10 18:00:58	123456789
👑 Команды администратора
/admin - открыть админ-панель

/today - записи на сегодня

/stats - статистика

/masters - список мастеров

📱 Команды пользователя
/start - начать работу с ботом

📅 Записаться - запись на услугу

👩 Наши мастера - список мастеров

📞 Контакты - контакты салона

ℹ️ О нас - информация о салоне

🔧 Настройка Google Sheets
Создайте новую Google таблицу

Создайте листы: masters и schedule

Настройте заголовки как указано выше

Добавьте мастеров в лист masters

Получите URL таблицы

Создайте сервисный аккаунт Google и скачайте credentials.json

Добавьте сервисный аккаунт в редакторы таблицы

📄 Лицензия
MIT

👨‍💻 Автор
Намесов Алексей
Если проект оказался полезным, поставьте звездочку!
