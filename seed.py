import sqlite3
from faker import Faker
import random
import os
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Database path
DB_PATH = os.getenv('DB_PATH', 'task_management.db')

def create_connection():
    """Create a database connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def populate_users(conn, num_users=20):
    """Populate users table with random data"""
    cursor = conn.cursor()
    
    print("Populating users...")
    users = []
    for _ in range(num_users):
        fullname = fake.name()
        email = fake.unique.email()
        is_active = random.choice([0, 1])
        users.append((fullname, email, is_active))
    
    cursor.executemany(
        "INSERT INTO users (fullname, email, is_active) VALUES (?, ?, ?)",
        users
    )
    conn.commit()
    print(f"Created {num_users} users")
    # Get the first user ID
    cursor.execute("SELECT MIN(id) FROM users")
    return cursor.fetchone()[0]

def populate_tasks(conn, num_tasks=50):
    """Populate tasks table with random data"""
    cursor = conn.cursor()
    
    print("Populating tasks...")
    
    # Get all user IDs
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all status IDs
    cursor.execute("SELECT id FROM status")
    status_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all priority IDs
    cursor.execute("SELECT id FROM priority")
    priority_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all category IDs
    cursor.execute("SELECT id FROM category")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    # Create tasks
    tasks = []
    for i in range(num_tasks):
        title = fake.sentence(nb_words=6)[:100]
        
        # Some tasks have empty description (for testing)
        if random.random() < 0.1:
            description = None
        else:
            description = fake.text(max_nb_chars=200)
        
        status_id = random.choice(status_ids)
        priority_id = random.choice(priority_ids)
        category_id = random.choice(category_ids + [None])  # Some tasks have no category
        user_id = random.choice(user_ids)
        
        # Due date from past month to next 3 months
        days_offset = random.randint(-30, 90)
        due_date = (datetime.now() + timedelta(days=days_offset)).strftime('%Y-%m-%d')
        
        # If status is completed, set completed_at
        cursor.execute("SELECT name FROM status WHERE id = ?", (status_id,))
        result = cursor.fetchone()
        if result is None:
            print(f"Warning: Status ID {status_id} not found")
            status_name = 'new'
        else:
            status_name = result[0]
        
        if status_name == 'completed':
            completed_at = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d %H:%M:%S')
        else:
            completed_at = None
        
        tasks.append((title, description, status_id, priority_id, category_id, user_id, due_date, completed_at))
    
    cursor.executemany(
        """INSERT INTO tasks (title, description, status_id, priority_id, category_id, user_id, due_date, completed_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        tasks
    )
    conn.commit()
    print(f"Created {num_tasks} tasks")

def populate_comments(conn, num_comments=100):
    """Populate comments table with random data"""
    cursor = conn.cursor()
    
    print("Populating comments...")
    
    # Get all task IDs
    cursor.execute("SELECT id FROM tasks")
    task_ids = [row[0] for row in cursor.fetchall()]
    
    # Get all user IDs
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Create comments
    comments = []
    for _ in range(num_comments):
        task_id = random.choice(task_ids)
        user_id = random.choice(user_ids)
        content = fake.text(max_nb_chars=150)
        comments.append((task_id, user_id, content))
    
    cursor.executemany(
        "INSERT INTO comments (task_id, user_id, content) VALUES (?, ?, ?)",
        comments
    )
    conn.commit()
    print(f"Created {num_comments} comments")

def ensure_users_without_tasks(conn):
    """Ensure some users have no tasks (for testing query 4)"""
    cursor = conn.cursor()
    
    # Get users with tasks
    cursor.execute("SELECT DISTINCT user_id FROM tasks")
    users_with_tasks = set(row[0] for row in cursor.fetchall())
    
    # Get all users
    cursor.execute("SELECT id FROM users")
    all_users = set(row[0] for row in cursor.fetchall())
    
    # Find users without tasks
    users_without_tasks = all_users - users_with_tasks
    
    # If all users have tasks, remove tasks from some users
    if len(users_without_tasks) == 0:
        # Get 3 random users to make taskless
        users_to_clear = random.sample(list(all_users), 3)
        for user_id in users_to_clear:
            cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
        conn.commit()
        print(f"Ensured {len(users_to_clear)} users have no tasks")

def main():
    """Main function to populate the database"""
    print("Starting database population...")
    
    conn = create_connection()
    
    try:
        # Populate tables
        populate_users(conn, num_users=20)
        populate_tasks(conn, num_tasks=50)
        populate_comments(conn, num_comments=100)
        ensure_users_without_tasks(conn)
        
        print("\nDatabase populated successfully!")
        
    except Exception as e:
        import traceback
        print(f"Error populating database: {e}")
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
