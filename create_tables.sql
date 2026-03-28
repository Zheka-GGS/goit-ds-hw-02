-- SQL script to create tables for task management system

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Create status table
CREATE TABLE IF NOT EXISTS status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (status_id) REFERENCES status(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert default status values
INSERT OR IGNORE INTO status (name) VALUES
('new'),
('in progress'),
('completed');

-- Ensure unique constraint on status name
CREATE UNIQUE INDEX IF NOT EXISTS idx_status_name ON status(name);
-- Ensure unique constraint on user email
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON users(email);