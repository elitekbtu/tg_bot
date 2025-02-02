CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    surname TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    number_of_tickets INT DEFAULT 0
);