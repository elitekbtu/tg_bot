# Конкурс Бот 🎉

## Описание
Приветствую! 👋 Это бот для участия в конкурсах. Он позволяет пользователям получать билеты за покупки и следить за результатами конкурсов.

## Функциональность
- 💰 *Стоимость билета:* 7900 ТГ за участие
- 📜 *Правила конкурса:*
  - Ваш чек должен включать сумму *не менее* 7900 ТГ.
  - Если сумма чека, например, 15800 ТГ, вы получите *2 билета* и так далее.
  - Для участия отправьте чек в формате *PDF*.

## Команды меню 📌
- 🎫 `/Мои билеты` – Показывает количество билетов, накопленных за все время.
- 🎟️ `/Получить билеты` – Отправьте чек и получите свои билеты!
- 🏆 `/Результаты` – Узнайте результаты прошедших и будущих конкурсов!

👇 Нажмите *«Получить билет»*, чтобы участвовать! 👇
🔔 Следите за обновлениями и не пропустите объявления о новых конкурсах! 🔔

---

## Настройка окружения
Создайте файл `.env` на основе `env.example` и укажите нужные параметры.

### `env.example`
```
BOT_TOKEN=your-bot-token

DB_HOST=localhost
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password

ADMIN_USER_ID=your_admin_user
```

## Установка зависимостей
Убедитесь, что у вас установлен Python. Затем установите зависимости с помощью:
```
pip install -r requirements.txt
```

### `requirements.txt`
```
telebot
psycopg2
python-dotenv
openpyxl
PyPDF2
logging
```

## Запуск бота
Запустите бота командой:
```
python main.py
```
