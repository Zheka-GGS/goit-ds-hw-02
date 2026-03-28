import sqlite3
from faker import Faker
import random
import os

# Ініціалізація Faker для генерації випадкових даних
fake = Faker()
# Встановлення шляху до бази даних через змінну середовища DB_PATH = os.getenv('DB_PATH', 'task_management.db')
def create_connection(db_path=None):
    """Create a database connection to the SQLite database"""
    if db_path is None:
        db_path = os.getenv('DB_PATH', 'task_management.db')
    conn = sqlite3.connect(db_path)
    return conn
# Функції для заповнення таблиць випадковими даними для користувачів та завдань з використанням Faker та випадкового вибору статусів та користувачів для завдань.
def populate_users(conn, num_users=10):
    """Populate the users table with random data"""
    cursor = conn.cursor()
    
    for _ in range(num_users):
        fullname = fake.name()
        email = fake.email()
        
        try:
            cursor.execute("INSERT INTO users (fullname, email) VALUES (?, ?)", (fullname, email))
        except sqlite3.IntegrityError:
            # Handle duplicate email case
            continue
    
    conn.commit()
# Функція для заповнення таблиці завдань випадковими даними, включаючи випадковий вибір статусу та користувача для кожного завдання.
def populate_tasks(conn, num_tasks=30):
    """Populate the tasks table with random data"""
    cursor = conn.cursor()
    
    # Get all user IDs
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all status IDs
    cursor.execute("SELECT id FROM status")
    status_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(num_tasks):
        title = fake.sentence(nb_words=4)
        description = fake.text(max_nb_chars=200)
        status_id = random.choice(status_ids)
        user_id = random.choice(user_ids)
        
        cursor.execute("""
            INSERT INTO tasks (title, description, status_id, user_id) 
            VALUES (?, ?, ?, ?)
        """, (title, description, status_id, user_id))
    
    conn.commit()
# Головна функція для запуску процесу заповнення бази даних. Вона створює з'єднання з базою даних, викликає функції для заповнення користувачів та завдань, а потім закриває з'єднання.
def main():
    """Main function to populate the database"""
    conn = create_connection()
    
    print("Populating users...")
    populate_users(conn)
    
    print("Populating tasks...")
    populate_tasks(conn)
    
    print("Database populated successfully!")
    
    conn.close()

if __name__ == "__main__":
    main()