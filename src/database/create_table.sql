CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    surname VARCHAR(255),
    name VARCHAR(255),
    address VARCHAR(255),
    phone_number VARCHAR(20),
    number_of_tickets INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    bill_number VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);