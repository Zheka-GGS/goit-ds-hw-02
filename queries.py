import sqlite3
import os
from datetime import datetime

def create_connection(db_path=None):
    """Create a database connection to the SQLite database"""
    if db_path is None:
        db_path = os.getenv('DB_PATH', 'task_management.db')
    conn = sqlite3.connect(db_path)
    return conn

def query_1_get_user_tasks(conn, user_id):
    """
    1. Отримати всі завдання певного користувача
    
    Args:
        conn: Database connection
        user_id: User ID
        
    Returns:
        List of tasks with status, priority, and category information
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, s.name AS status_name, p.name AS priority_name, c.name AS category_name
        FROM tasks t
        JOIN status s ON t.status_id = s.id
        JOIN priority p ON t.priority_id = p.id
        LEFT JOIN category c ON t.category_id = c.id
        WHERE t.user_id = ?
    """, (user_id,))
    return cursor.fetchall()

def query_2_get_tasks_by_status(conn, status_name):
    """
    2. Вибрати завдання за певним статусом
    
    Args:
        conn: Database connection
        status_name: Status name (e.g., 'new')
        
    Returns:
        List of tasks with the specified status
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* FROM tasks t
        WHERE t.status_id = (SELECT id FROM status WHERE name = ?)
    """, (status_name,))
    return cursor.fetchall()

def query_3_update_task_status(conn, task_id, new_status_name):
    """
    3. Оновити статус конкретного завдання
    
    Args:
        conn: Database connection
        task_id: Task ID
        new_status_name: New status name
        
    Returns:
        None
    """
    cursor = conn.cursor()
    
    # Get the new status ID
    cursor.execute("SELECT id FROM status WHERE name = ?", (new_status_name,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Status '{new_status_name}' not found")
    new_status_id = result[0]
    
    # Update the task status
    if new_status_name == 'completed':
        cursor.execute("""
            UPDATE tasks 
            SET status_id = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_status_id, task_id))
    else:
        cursor.execute("""
            UPDATE tasks 
            SET status_id = ?
            WHERE id = ?
        """, (new_status_id, task_id))
    
    conn.commit()

def query_4_get_users_without_tasks(conn):
    """
    4. Отримати список користувачів, які не мають жодного завдання
    
    Args:
        conn: Database connection
        
    Returns:
        List of users without tasks
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users 
        WHERE id NOT IN (SELECT DISTINCT user_id FROM tasks WHERE user_id IS NOT NULL)
    """)
    return cursor.fetchall()

def query_5_add_new_task(conn, title, description, user_id, status_name='new', priority_name='medium', category_name=None, due_date=None):
    """
    5. Додати нове завдання для конкретного користувача
    
    Args:
        conn: Database connection
        title: Task title
        description: Task description
        user_id: User ID
        status_name: Status name (default: 'new')
        priority_name: Priority name (default: 'medium')
        category_name: Category name (optional)
        due_date: Due date in YYYY-MM-DD format (optional)
        
    Returns:
        ID of the newly created task
    """
    cursor = conn.cursor()
    
    # Get status ID
    cursor.execute("SELECT id FROM status WHERE name = ?", (status_name,))
    status_id = cursor.fetchone()[0]
    
    # Get priority ID
    cursor.execute("SELECT id FROM priority WHERE name = ?", (priority_name,))
    priority_id = cursor.fetchone()[0]
    
    # Get category ID if provided
    category_id = None
    if category_name:
        cursor.execute("SELECT id FROM category WHERE name = ?", (category_name,))
        result = cursor.fetchone()
        if result:
            category_id = result[0]
    
    cursor.execute("""
        INSERT INTO tasks (title, description, status_id, priority_id, category_id, user_id, due_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, status_id, priority_id, category_id, user_id, due_date))
    
    conn.commit()
    return cursor.lastrowid

def query_6_get_uncompleted_tasks(conn):
    """
    6. Отримати всі завдання, які ще не завершено
    
    Args:
        conn: Database connection
        
    Returns:
        List of uncompleted tasks
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* FROM tasks t 
        JOIN status s ON t.status_id = s.id 
        WHERE s.name NOT IN ('completed', 'cancelled')
    """)
    return cursor.fetchall()

def query_7_delete_task(conn, task_id):
    """
    7. Видалити конкретне завдання
    
    Args:
        conn: Database connection
        task_id: Task ID
        
    Returns:
        None
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

def query_8_find_users_by_email(conn, email_pattern):
    """
    8. Знайти користувачів з певною електронною поштою
    
    Args:
        conn: Database connection
        email_pattern: Email pattern (e.g., '%@gmail.com')
        
    Returns:
        List of users matching the email pattern
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email LIKE ?", (email_pattern,))
    return cursor.fetchall()

def query_9_update_user_name(conn, new_fullname, user_id):
    """
    9. Оновити ім'я користувача
    
    Args:
        conn: Database connection
        new_fullname: New full name
        user_id: User ID
        
    Returns:
        None
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET fullname = ? WHERE id = ?", (new_fullname, user_id))
    conn.commit()

def query_10_get_task_count_by_status(conn):
    """
    10. Отримати кількість завдань для кожного статусу
    
    Args:
        conn: Database connection
        
    Returns:
        List of tuples (status_name, task_count)
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.name, COUNT(t.id) AS task_count 
        FROM status s 
        LEFT JOIN tasks t ON s.id = t.status_id 
        GROUP BY s.id, s.name
    """)
    return cursor.fetchall()

def query_11_get_tasks_by_domain(conn, domain_pattern):
    """
    11. Отримати завдання, які призначені користувачам з певною доменною частиною електронної пошти
    
    Args:
        conn: Database connection
        domain_pattern: Domain pattern (e.g., '%@example.com')
        
    Returns:
        List of tasks assigned to users with matching email domain
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* 
        FROM tasks t 
        JOIN users u ON t.user_id = u.id 
        WHERE u.email LIKE ?
    """, (domain_pattern,))
    return cursor.fetchall()

def query_12_get_tasks_without_description(conn):
    """
    12. Отримати список завдань, що не мають опису
    
    Args:
        conn: Database connection
        
    Returns:
        List of tasks without description
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE description IS NULL OR description = ''")
    return cursor.fetchall()

def query_13_get_users_and_inprogress_tasks(conn):
    """
    13. Вибрати користувачів та їхні завдання, які є у статусі 'in progress'
    
    Args:
        conn: Database connection
        
    Returns:
        List of tuples (user_name, task_title, task_description, status_name)
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.fullname, t.title, t.description, s.name AS status_name
        FROM users u
        JOIN tasks t ON u.id = t.user_id
        JOIN status s ON t.status_id = s.id
        WHERE s.name = 'in progress'
    """)
    return cursor.fetchall()

def query_14_get_users_and_task_counts(conn):
    """
    14. Отримати користувачів та кількість їхніх завдань
    
    Args:
        conn: Database connection
        
    Returns:
        List of tuples (user_name, task_count)
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.fullname, COUNT(t.id) AS task_count
        FROM users u
        LEFT JOIN tasks t ON u.id = t.user_id
        GROUP BY u.id, u.fullname
    """)
    return cursor.fetchall()

def query_15_get_highest_priority_tasks(conn):
    """
    15. Отримати завдання з найвищим пріоритетом
    
    Args:
        conn: Database connection
        
    Returns:
        List of tasks with 'critical' or 'high' priority, sorted by due date
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, p.name AS priority_name
        FROM tasks t
        JOIN priority p ON t.priority_id = p.id
        WHERE p.name IN ('critical', 'high')
        ORDER BY t.due_date ASC
    """)
    return cursor.fetchall()

def query_16_get_overdue_tasks(conn):
    """
    16. Отримати прострочені завдання
    
    Args:
        conn: Database connection
        
    Returns:
        List of overdue tasks
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, s.name AS status_name
        FROM tasks t
        JOIN status s ON t.status_id = s.id
        WHERE t.due_date < DATE('now')
        AND s.name NOT IN ('completed', 'cancelled')
    """)
    return cursor.fetchall()

def query_17_get_task_statistics_by_category(conn):
    """
    17. Отримати статистику завдань по категоріях
    
    Args:
        conn: Database connection
        
    Returns:
        List of tuples (category_name, task_count)
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, COUNT(t.id) AS task_count
        FROM category c
        LEFT JOIN tasks t ON c.id = t.category_id
        GROUP BY c.id, c.name
    """)
    return cursor.fetchall()

def query_18_get_latest_comments(conn, task_id, limit=5):
    """
    18. Отримати останні коментарі до завдання
    
    Args:
        conn: Database connection
        task_id: Task ID
        limit: Number of comments to return (default: 5)
        
    Returns:
        List of latest comments for the task
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, u.fullname AS user_name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.task_id = ?
        ORDER BY c.created_at DESC
        LIMIT ?
    """, (task_id, limit))
    return cursor.fetchall()

def query_19_get_users_with_most_inprogress_tasks(conn, limit=5):
    """
    19. Отримати користувачів з найбільшою кількістю завдань у статусі 'in progress'
    
    Args:
        conn: Database connection
        limit: Number of users to return (default: 5)
        
    Returns:
        List of tuples (user_name, in_progress_count)
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.fullname, COUNT(t.id) AS in_progress_count
        FROM users u
        JOIN tasks t ON u.id = t.user_id
        JOIN status s ON t.status_id = s.id
        WHERE s.name = 'in progress'
        GROUP BY u.id, u.fullname
        ORDER BY in_progress_count DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()

def query_20_get_average_completion_time(conn):
    """
    20. Отримати середній час виконання завдань
    
    Args:
        conn: Database connection
        
    Returns:
        Average completion time in days
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(JULIANDAY(completed_at) - JULIANDAY(created_at)) AS avg_days
        FROM tasks
        WHERE completed_at IS NOT NULL
    """)
    result = cursor.fetchone()
    return result[0] if result[0] else 0
