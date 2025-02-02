import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import psycopg2
from dotenv import load_dotenv
import os
import openpyxl
import re
import PyPDF2
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Database connection details from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Initialize the bot with your token
bot = telebot.TeleBot(BOT_TOKEN)

# Admin user ID (you can store this in your .env file too)
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "YOUR_ADMIN_USER_ID")

# Check if all necessary environment variables are set
if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, ADMIN_USER_ID]):
    raise ValueError("Missing one or more required environment variables.")

# Connect to PostgreSQL database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to read SQL queries from files
def read_sql_file(filename):
    file_path = os.path.join("src/database", filename)
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The SQL file '{file_path}' was not found.")

# Create a table for user registration if it doesn't exist
def create_user_table():
    conn = connect_to_db()
    if conn:
        try:
            create_table_query = read_sql_file("create_table.sql")
            cur = conn.cursor()
            cur.execute(create_table_query)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error creating table: {e}")

# Function to register a user in the database
def register_user(user_id, surname, name, address, phone_number):
    conn = connect_to_db()
    if conn:
        try:
            insert_query = read_sql_file("insert.sql")
            cur = conn.cursor()
            cur.execute(insert_query, (user_id, surname, name, address, phone_number, 0))  # Add 0 for number_of_tickets
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
    return False

def send_menu(message):
    user_id = message.from_user.id
    if str(user_id) == ADMIN_USER_ID:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=create_admin_menu())
    else:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=create_menu())

# Function to check if the user is registered
def check_user_registration(user_id):
    conn = connect_to_db()
    if conn:
        try:
            select_query = read_sql_file("select.sql")
            cur = conn.cursor()
            cur.execute(select_query, (user_id,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            return user
        except Exception as e:
            print(f"Error checking user registration: {e}")
    return None

# Function to generate an Excel file with user data
def generate_excel_report(users):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users and Tickets"

    # Add headers for user data
    headers = ["User ID", "Surname", "Name", "Address", "Phone Number", "Number of Tickets", "Ticket ID", "Ticket Date"]
    ws.append(headers)

    # Add user data and their tickets
    for user in users:
        user_id = user[0]
        user_data = list(user[:6])  # User data without tickets
        tickets = get_user_tickets(user_id)
        
        if tickets:
            for ticket in tickets:
                ticket_data = [ticket[0], ticket[1].strftime('%d.%m.%Y %H:%M')]  # Ticket ID and Date
                ws.append(user_data + ticket_data)
        else:
            ws.append(user_data + ["No tickets", "N/A"])

    # Save to an in-memory byte stream (to send it as a file)
    byte_stream = BytesIO()
    wb.save(byte_stream)
    byte_stream.seek(0)

    # Create a file-like object with the correct extension
    byte_stream.name = "user_tickets_data.xlsx"  # Explicitly set the file name
    return byte_stream

# Function to fetch all users from the database
def get_all_users():
    conn = connect_to_db()
    if conn:
        try:
            select_query = "SELECT * FROM users"
            cur = conn.cursor()
            cur.execute(select_query)
            users = cur.fetchall()
            cur.close()
            conn.close()
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    return []

# Function to fetch all users from the database
def get_all_users():
    conn = connect_to_db()
    if conn:
        try:
            select_query = "SELECT * FROM users"
            cur = conn.cursor()
            cur.execute(select_query)
            users = cur.fetchall()
            cur.close()
            conn.close()
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    return []

# Function to read a file and return its content
def file_reader(filename):
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{filename}' was not found.")

# Function to create the custom keyboard menu
def create_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(KeyboardButton("Мои билеты"), KeyboardButton("Получить билеты"), KeyboardButton("Результаты"))
    return menu

def create_admin_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(KeyboardButton("Мои билеты"), KeyboardButton("Получить билеты"), KeyboardButton("Результаты"))
    menu.add(KeyboardButton("Экспорт данных"), KeyboardButton("Управление пользователями"))
    return menu
def return_to_menu(chat_id, user_id):
    if str(user_id) == ADMIN_USER_ID:
        bot.send_message(chat_id, "Возврат в главное меню:", reply_markup=create_admin_menu())
    else:
        bot.send_message(chat_id, "Возврат в главное меню:", reply_markup=create_menu())
@bot.message_handler(commands=['start'])
def main(message):
    user_id = message.from_user.id  # Get the user ID
    try:
        welcome_text = file_reader("WELCOME.md")
        if str(user_id) == ADMIN_USER_ID:
            bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=create_admin_menu())
        else:
            bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=create_menu())
    except FileNotFoundError:
        default_welcome_message = (
            "🎟 <b>Добро пожаловать в Конкурс Бот!</b> 🎟\n\n"
            "Привет! Я помогу вам получить билет для участия в захватывающих конкурсах. 🎉\n\n"
            "💰 <b>Стоимость билета:</b> 7900 ТГ за участие\n"
            "📜 <b>Правила конкурса:</b>\n\n"
            "Ваш билет должен включать не менее 7900 ТГ.\n"
            "Если сумма, указанная в билете, например, 15800 ТГ, у вас будет 2 билета и так далее.\n"
            "Для участия в конкурсе отправьте чек в формате PDF.\n\n"
            "📌 <b>Команды:</b>\n"
            "🔹 <i>Мои билеты</i> – Показывает количество билетов за все время.\n"
            "🔹 <i>Получить билеты</i> – Получить билеты.\n"
            "🔹 <i>Результаты</i> – Результаты конкурса.\n\n"
            "✅ Нажмите <b>Получить билет</b>, чтобы участвовать!\n"
            "🔔 Следите за обновлениями и объявлениями!\n\n"
            "Начнем—нажмите кнопку ниже! 👇")
        if str(user_id) == ADMIN_USER_ID:
            bot.send_message(message.chat.id, default_welcome_message, parse_mode='HTML', reply_markup=create_admin_menu())
        else:
            bot.send_message(message.chat.id, default_welcome_message, parse_mode='HTML', reply_markup=create_menu())

    user = check_user_registration(user_id)
    if not user:
        bot.send_message(message.chat.id, "Для регистрации введите следующие данные:")
        bot.send_message(message.chat.id, "Введите вашу фамилию:")
        bot.register_next_step_handler(message, ask_surname)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы! 🎉")
        return_to_menu(message.chat.id, message.from_user.id)
    
# Handler for the "Экспорт данных" button (admin only)
@bot.message_handler(func=lambda message: message.text == "Экспорт данных")
def export_data(message):
    if str(message.from_user.id) == ADMIN_USER_ID:
        users = get_all_users()
        if users:
            excel_file = generate_excel_report(users)
            bot.send_document(message.chat.id, excel_file, caption="User and Tickets Data Report")
        else:
            bot.send_message(message.chat.id, "No users found in the database.")
    else:
        bot.send_message(message.chat.id, "You do not have permission to perform this action.")

# Handler for the "Управление пользователями" button (admin only)
@bot.message_handler(func=lambda message: message.text == "Управление пользователями")
def manage_users(message):
    if str(message.from_user.id) == ADMIN_USER_ID:
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=create_admin_management_menu())
    else:
        bot.send_message(message.chat.id, "You do not have permission to perform this action.")

# Function to create the admin management menu
def create_admin_management_menu():
    menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(KeyboardButton("Добавить пользователя"), KeyboardButton("Удалить пользователя"))
    menu.add(KeyboardButton("Назад"))
    return menu

# Handler for the "Добавить пользователя" button (admin only)
@bot.message_handler(func=lambda message: message.text == "Добавить пользователя")
def add_user(message):
    if str(message.from_user.id) == ADMIN_USER_ID:
        bot.send_message(message.chat.id, "Введите ID пользователя для добавления:")
        bot.register_next_step_handler(message, process_add_user)
    else:
        bot.send_message(message.chat.id, "You do not have permission to perform this action.")

# Function to process adding a user
def process_add_user(message):
    user_id = message.text
    # Add logic to add the user to the database
    bot.send_message(message.chat.id, f"Пользователь с ID {user_id} добавлен.")

# Handler for the "Удалить пользователя" button (admin only)
@bot.message_handler(func=lambda message: message.text == "Удалить пользователя")
def delete_user(message):
    if str(message.from_user.id) == ADMIN_USER_ID:
        bot.send_message(message.chat.id, "Введите ID пользователя для удаления:")
        bot.register_next_step_handler(message, process_delete_user)
    else:
        bot.send_message(message.chat.id, "You do not have permission to perform this action.")

# Function to process deleting a user
def process_delete_user(message):
    user_id = message.text
    # Add logic to delete the user from the database
    bot.send_message(message.chat.id, f"Пользователь с ID {user_id} удален.")

# Handler for the "Назад" button (admin only)
@bot.message_handler(func=lambda message: message.text == "Назад")
def back_to_main_menu(message):
    if str(message.from_user.id) == ADMIN_USER_ID:
        bot.send_message(message.chat.id, "Возврат в главное меню:", reply_markup=create_admin_menu())
    else:
        bot.send_message(message.chat.id, "You do not have permission to perform this action.")

# Function to ask for surname
def ask_surname(message):
    user_id = message.from_user.id
    surname = message.text
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, ask_name, surname)

# Function to ask for name
def ask_name(message, surname):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(message.chat.id, "Введите ваш адрес (Город, район, улица, номер квартиры):")
    bot.register_next_step_handler(message, ask_address, surname, name)

# Function to ask for address
def ask_address(message, surname, name):
    user_id = message.from_user.id
    address = message.text
    bot.send_message(message.chat.id, "Введите ваш номер телефона: (8 ### ### ## ##)")
    bot.register_next_step_handler(message, ask_phone_number, surname, name, address)

# Function to ask for phone number and complete registration
def ask_phone_number(message, surname, name, address):
    user_id = message.from_user.id
    phone_number = message.text
    user = check_user_registration(user_id)
    if user:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы! 🎉")
        return
    if register_user(user_id, surname, name, address, phone_number):
        bot.send_message(message.chat.id, "Регистрация успешно завершена! 🎉")
    else:
        bot.send_message(message.chat.id, "Ошибка при регистрации. Пожалуйста, попробуйте снова.")

def update_tickets(user_id, bill_amount, bill_number):
    conn = connect_to_db()
    if conn:
        try:
            tickets_count = bill_amount // 7900
            cur = conn.cursor()

            # Проверка, существует ли уже такой чек для этого пользователя
            check_ticket_query = "SELECT 1 FROM tickets WHERE user_id = %s AND bill_number = %s"
            cur.execute(check_ticket_query, (user_id, bill_number))
            existing_ticket = cur.fetchone()

            if existing_ticket:
                bot.send_message(user_id, "Вы уже добавили этот чек.")
                return 0

            # Добавление билетов
            insert_ticket_query = "INSERT INTO tickets (user_id, bill_number) VALUES (%s, %s)"
            for _ in range(tickets_count):
                cur.execute(insert_ticket_query, (user_id, bill_number))

            # Обновление общего количества билетов пользователя
            update_user_query = """
                UPDATE users 
                SET number_of_tickets = number_of_tickets + %s 
                WHERE user_id = %s
            """
            cur.execute(update_user_query, (tickets_count, user_id))

            conn.commit()
            return tickets_count

        except psycopg2.IntegrityError as e:
            print(f"Ошибка уникальности: {e}")
            bot.send_message(user_id, "Этот чек уже был использован другим пользователем.")
            return 0
        except Exception as e:
            print(f"Ошибка при обновлении билетов: {e}")
            bot.send_message(user_id, "Произошла ошибка при обработке чека. Пожалуйста, попробуйте позже.")
            return 0
        finally:
            cur.close()
            conn.close()
    return 0

def get_user_tickets(user_id):
    conn = connect_to_db()
    if conn:
        try:
            query = """
                SELECT 
                    t.ticket_id,
                    t.created_at,
                    u.surname,
                    u.name
                FROM tickets t
                JOIN users u ON t.user_id = u.user_id
                WHERE t.user_id = %s
                ORDER BY t.ticket_id
            """
            cur = conn.cursor()
            cur.execute(query, (user_id,))
            tickets = cur.fetchall()
            return tickets
        except Exception as e:
            print(f"Error fetching tickets: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    return []


# Handler for the "Мои билеты" button
@bot.message_handler(func=lambda message: message.text == "Мои билеты")
def my_tickets(message):
    user_id = message.from_user.id
    user = check_user_registration(user_id)
    
    if not user:
        bot.send_message(message.chat.id, "Вы не зарегистрированы❌")
        return
    
    tickets = get_user_tickets(user_id)
    response = [
        f"🎫 Ваши билеты (всего {len(tickets)}):",
        *[f"ID: {t[0]} | Дата: {t[1].strftime('%d.%m.%Y %H:%M')}" for t in tickets],
        "➖➖➖➖➖➖➖➖➖➖➖➖➖"
    ]
    bot.send_message(message.chat.id, "\n".join(response))
    return_to_menu(message.chat.id, message.from_user.id)


# Handler for the "Получить билеты" button
@bot.message_handler(func=lambda message: message.text == "Получить билеты")
def get_tickets(message):
    user_id = message.from_user.id
    user = check_user_registration(user_id)
    
    if not user:
        bot.send_message(message.chat.id, "Вы не зарегистрированы❌")
        return
    
    bot.send_message(message.chat.id, "Отправьте чек с суммой, чтобы получить билеты.")

# Handler for the "Результаты" button
@bot.message_handler(func=lambda message: message.text == "Результаты")
def results(message):
    bot.send_message(message.chat.id, "Результаты конкурса будут опубликованы позже.")

# Handler for the /export_users command (admin only)
@bot.message_handler(commands=['export_users'])
def export_users(message):
    if message.from_user.id == int(ADMIN_USER_ID):  # Check if the user is the admin
        users = get_all_users()
        if users:
            excel_file = generate_excel_report(users)
            bot.send_document(message.chat.id, excel_file, caption="User Data Report", file_name="user_data.xlsx")
        else:
            bot.send_message(message.chat.id, "No users found in the database.")
    else:
        bot.send_message(message.chat.id, "You do not have permission to perform this action.")

# Функция для извлечения текста из PDF-файла
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)  # Используем PdfReader вместо PdfFileReader
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Функция для извлечения данных из чека
def extract_receipt_data(text):
    # Регулярные выражения для извлечения данных
    amount_pattern = amount_pattern = r"(\d{1,3}(?: \d{3})*|\d+) ? ₸"
    date_pattern = r"(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2})"
    name_pattern = r"([А-Яа-я]+\s[А-Яа-я]+\.)"
    number_pattern = r"№ чека ([A-Z]{2}\d{10})"

    amount = re.search(amount_pattern, text)
    date = re.search(date_pattern, text)
    name = re.search(name_pattern, text)
    number = re.search(number_pattern, text)

    return {
        "amount": amount.group(1) if amount else None,
        "date": date.group(1) if date else None,
        "name": name.group(1) if name else None,
        "number": number.group(1) if number else None,
    }

# Обработчик для получения PDF-файла от пользователя
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type == 'application/pdf':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        pdf_file = BytesIO(downloaded_file)

        # Извлечение текста из PDF
        text = extract_text_from_pdf(pdf_file)
        # Извлечение данных из чека
        receipt_data = extract_receipt_data(text)

        if receipt_data["amount"] and receipt_data["number"]:
            amount = int(receipt_data["amount"].replace(" ", "").replace(",", ""))
            bill_number = receipt_data["number"]
            user_id = message.from_user.id
            tickets = update_tickets(user_id, amount, bill_number)

            if tickets > 0:
                bot.send_message(message.chat.id, f"Вы получили {tickets} билетов! 🎟")
            else:
                bot.send_message(message.chat.id, "Не удалось добавить билеты. Пожалуйста, убедитесь, что сумма корректна.")
        else:
            bot.send_message(message.chat.id, "Не удалось извлечь данные из чека. Пожалуйста, убедитесь, что чек корректный.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте чек в формате PDF.")
        return_to_menu(message.chat.id, message.from_user.id)
# Start polling for messages
bot.polling(non_stop=True)