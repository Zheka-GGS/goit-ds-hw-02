import sqlite3
from faker import Faker
import random
import os

def create_connection(db_path=None):
    """Create a database connection to the SQLite database"""
    if db_path is None:
        db_path = os.getenv('DB_PATH', 'task_management.db')
    conn = sqlite3.connect(db_path)
    return conn

def test_query_1_get_user_tasks(conn, user_id):
    """1. Отримати всі завдання певного користувача"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def test_query_2_get_tasks_by_status(conn, status_name):
    """2. Вибрати завдання за певним статусом"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* FROM tasks t
        JOIN status s ON t.status_id = s.id
        WHERE s.name = ?
    """, (status_name,))
    return cursor.fetchall()

def test_query_3_update_task_status(conn, task_id, new_status_name):
    """3. Оновити статус конкретного завдання"""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks 
        SET status_id = (SELECT id FROM status WHERE name = ?) 
        WHERE id = ?
    """, (new_status_name, task_id))
    conn.commit()

def test_query_4_get_users_without_tasks(conn):
    """4. Отримати список користувачів, які не мають жодного завдання"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users 
        WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks WHERE user_id IS NOT NULL)
    """)
    return cursor.fetchall()

def test_query_5_add_new_task(conn, title, description, user_id, status_name='new'):
    """5. Додати нове завдання для конкретного користувача"""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, status_id, user_id) 
        VALUES (?, ?, (SELECT id FROM status WHERE name = ?), ?)
    """, (title, description, status_name, user_id))
    conn.commit()

def test_query_6_get_uncompleted_tasks(conn):
    """6. Отримати всі завдання, які ще не завершено"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* FROM tasks t 
        JOIN status s ON t.status_id = s.id 
        WHERE s.name != 'completed'
    """)
    return cursor.fetchall()

def test_query_7_delete_task(conn, task_id):
    """7. Видалити конкретне завдання"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

def test_query_8_find_users_by_email(conn, email_pattern):
    """8. Знайти користувачів з певною електронною поштою"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email LIKE ?", (email_pattern,))
    return cursor.fetchall()

def test_query_9_update_user_name(conn, new_fullname, user_id):
    """9. Оновити ім'я користувача"""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET fullname = ? WHERE id = ?", (new_fullname, user_id))
    conn.commit()

def test_query_10_get_task_count_by_status(conn):
    """10. Отримати кількість завдань для кожного статусу"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, COUNT(t.id) AS task_count 
        FROM status s 
        LEFT JOIN tasks t ON s.id = t.status_id 
        GROUP BY s.id, s.name
    """)
    return cursor.fetchall()

def test_query_11_get_tasks_by_domain(conn, domain_pattern):
    """11. Отримати завдання, які призначені користувачам з певною доменною частиною електронної пошти"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* 
        FROM tasks t 
        JOIN users u ON t.user_id = u.id 
        WHERE u.email LIKE ?
    """, (domain_pattern,))
    return cursor.fetchall()

def test_query_12_get_tasks_without_description(conn):
    """12. Отримати список завдань, що не мають опису"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE description IS NULL OR description = ''")
    return cursor.fetchall()

def test_query_13_get_users_and_inprogress_tasks(conn):
    """13. Вибрати користувачів та їхні завдання, які є у статусі 'in progress'"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.fullname, t.title, t.description, s.name AS status_name
        FROM users u
        JOIN tasks t ON u.id = t.user_id
        JOIN status s ON t.status_id = s.id
        WHERE s.name = 'in progress'
    """)
    return cursor.fetchall()

def test_query_14_get_users_and_task_counts(conn):
    """14. Отримати користувачів та кількість їхніх завдань"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.fullname, COUNT(t.id) AS task_count
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        GROUP BY u.id, u.fullname
    """)
    return cursor.fetchall()

def main():
    """Main function to test all queries"""
    conn = create_connection()
    
    print("Testing all queries...")
    
    # Test query 1: Get all tasks for a specific user
    print("\n1. Tasks for user with ID 1:")
    tasks = test_query_1_get_user_tasks(conn, 1)
    for task in tasks[:5]:  # Show first 5 results
        print(f"  Task: {task}")
    
    # Test query 2: Get tasks by status
    print("\n2. Tasks with status 'new':")
    new_tasks = test_query_2_get_tasks_by_status(conn, 'new')
    for task in new_tasks[:5]:  # Show first 5 results
        print(f"  Task: {task}")
    
    # Test query 3: Update task status
    print("\n3. Updating task status:")
    if tasks:  # Use first task from query 1
        task_id = tasks[0][0]
        print(f"  Updating task {task_id} to 'in progress'")
        test_query_3_update_task_status(conn, task_id, 'in progress')
        print(f"  Task {task_id} updated successfully")
    
    # Test query 4: Get users without tasks
    print("\n4. Users without tasks:")
    users_no_tasks = test_query_4_get_users_without_tasks(conn)
    for user in users_no_tasks:
        print(f"  User: {user}")
    
    # Test query 5: Add new task
    print("\n5. Adding new task:")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users LIMIT 1")
    user_id = cursor.fetchone()[0]
    print(f"  Adding new task for user {user_id}")
    test_query_5_add_new_task(conn, "Test Task", "This is a test task description", user_id)
    print(f"  New task added successfully")
    
    # Test query 6: Get uncompleted tasks
    print("\n6. Uncompleted tasks:")
    uncompleted = test_query_6_get_uncompleted_tasks(conn)
    for task in uncompleted[:5]:  # Show first 5 results
        print(f"  Task: {task}")
    
    # Test query 8: Find users by email pattern
    print("\n8. Users with gmail addresses:")
    gmail_users = test_query_8_find_users_by_email(conn, '%@gmail.com')
    for user in gmail_users[:5]:  # Show first 5 results
        print(f"  User: {user}")
    
    # Test query 10: Get task count by status
    print("\n10. Task count by status:")
    counts = test_query_10_get_task_count_by_status(conn)
    for status, count in counts:
        print(f"  {status}: {count}")
    
    # Test query 11: Get tasks by domain
    print("\n11. Tasks assigned to users with 'example.com' domain:")
    domain_tasks = test_query_11_get_tasks_by_domain(conn, '%@example.com')
    for task in domain_tasks[:5]:  # Show first 5 results
        print(f"  Task: {task}")
    
    # Test query 12: Get tasks without description
    print("\n12. Tasks without description:")
    no_desc_tasks = test_query_12_get_tasks_without_description(conn)
    for task in no_desc_tasks[:5]:  # Show first 5 results
        print(f"  Task: {task}")
    
    # Test query 13: Get users and their in-progress tasks
    print("\n13. Users and their in-progress tasks:")
    in_progress = test_query_13_get_users_and_inprogress_tasks(conn)
    for item in in_progress[:5]:  # Show first 5 results
        print(f"  {item}")
    
    # Test query 14: Get users and their task counts
    print("\n14. Users and their task counts:")
    user_counts = test_query_14_get_users_and_task_counts(conn)
    for user, count in user_counts[:10]:  # Show first 10 results
        print(f"  {user}: {count} tasks")
    
    conn.close()
    print("\nAll queries tested successfully!")

if __name__ == "__main__":
    main()