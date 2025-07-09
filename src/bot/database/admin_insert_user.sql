INSERT INTO users (user_id, surname, name, address, phone_number, number_of_tickets)
VALUES (123456789, 'Admin', 'User', 'Admin Address', '+1234567890', 0)
ON CONFLICT (user_id) DO NOTHING;