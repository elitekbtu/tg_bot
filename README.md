# Конкурс Бот 🎉

## Описание

Это Telegram-бот для проведения конкурсов, где пользователи получают билеты за покупки и могут следить за результатами.

---

## Основные возможности

- **Стоимость билета:** 7900₸ за участие.
- **Правила конкурса:**
  - Чек должен быть минимум на 7900₸.
  - За каждый полный 7900₸ в чеке – 1 билет (например, 15800₸ = 2 билета).
  - Для участия отправьте чек в формате PDF.
- **Команды меню:**
  - `/Мои билеты` — показывает, сколько у вас билетов за всё время.
  - `/Получить билеты` — отправьте чек и получите билеты.
  - `/Результаты` — смотрите итоги завершённых и будущих конкурсов.

---

## Быстрый старт через Docker

1. **Создайте файл `.env` в корне проекта на основе `env.example`:**

   ```
   BOT_TOKEN=your-bot-token
   DB_HOST=localhost
   DB_NAME=your_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   ADMIN_USER_ID=your_admin_user
   ```

2. **Соберите Docker-образ:**

   ```
   docker build -t tg_bot .
   ```

3. **Запустите контейнер:**

   ```
   docker run --env-file .env --name tg_bot_container tg_bot
   ```

   Для запуска в фоне добавьте `-d`:
   ```
   docker run -d --env-file .env --name tg_bot_container tg_bot
   ```

---

## Альтернативный запуск без Docker

Установите зависимости:

```
pip install -r requirements.txt
```

Запустите бота:

```
python main.py
```

---

## Необходимые зависимости

- Python 3.8+
- Tesseract-OCR (для распознавания чеков)
- Библиотеки Python (см. `requirements.txt`):

  ```
  telebot
  psycopg2
  python-dotenv
  openpyxl
  PyPDF2
  logging
  ```
