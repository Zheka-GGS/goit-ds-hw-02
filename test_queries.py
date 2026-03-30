import unittest
import sqlite3
import os
from datetime import datetime, timedelta
from queries import (
    query_1_get_user_tasks,
    query_2_get_tasks_by_status,
    query_3_update_task_status,
    query_4_get_users_without_tasks,
    query_5_add_new_task,
    query_6_get_uncompleted_tasks,
    query_7_delete_task,
    query_8_find_users_by_email,
    query_9_update_user_name,
    query_10_get_task_count_by_status,
    query_11_get_tasks_by_domain,
    query_12_get_tasks_without_description,
    query_13_get_users_and_inprogress_tasks,
    query_14_get_users_and_task_counts,
    query_15_get_highest_priority_tasks,
    query_16_get_overdue_tasks,
    query_17_get_task_statistics_by_category,
    query_18_get_latest_comments,
    query_19_get_users_with_most_inprogress_tasks,
    query_20_get_average_completion_time
)

class TestQueries(unittest.TestCase):
    """Unit tests for all query functions"""
    
    def setUp(self):
        """Set up test database before each test"""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        # Enable foreign key support
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self.cursor.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );
            
            CREATE TABLE status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE
            );
            
            CREATE TABLE priority (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                level INTEGER NOT NULL UNIQUE
            );
            
            CREATE TABLE category (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE
            );
            
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                status_id INTEGER NOT NULL,
                priority_id INTEGER NOT NULL,
                category_id INTEGER,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date DATE,
                completed_at TIMESTAMP,
                FOREIGN KEY (status_id) REFERENCES status(id),
                FOREIGN KEY (priority_id) REFERENCES priority(id),
                FOREIGN KEY (category_id) REFERENCES category(id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CHECK (due_date IS NULL OR due_date >= DATE(created_at))
            );
            
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        
        # Insert test data
        self.cursor.executemany(
            "INSERT INTO status (name) VALUES (?)",
            [('new',), ('in progress',), ('completed',), ('on hold',), ('cancelled',)]
        )
        
        self.cursor.executemany(
            "INSERT INTO priority (name, level) VALUES (?, ?)",
            [('low', 1), ('medium', 2), ('high', 3), ('critical', 4)]
        )
        
        self.cursor.executemany(
            "INSERT INTO category (name) VALUES (?)",
            [('development',), ('testing',), ('documentation',)]
        )
        
        self.cursor.executemany(
            "INSERT INTO users (fullname, email, is_active) VALUES (?, ?, ?)",
            [
                ('John Doe', 'john@example.com', 1),
                ('Jane Smith', 'jane@gmail.com', 1),
                ('Bob Wilson', 'bob@example.com', 0),
                ('Alice Brown', 'alice@gmail.com', 1),
            ]
        )
        
        # Use future dates to satisfy CHECK constraint (due_date >= DATE(created_at))
        future_date_1 = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        future_date_2 = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
        future_date_3 = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        
        self.cursor.executemany(
            """INSERT INTO tasks (title, description, status_id, priority_id, category_id, user_id, due_date, completed_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                ('Task 1', 'Description 1', 1, 2, 1, 1, future_date_1, None),
                ('Task 2', 'Description 2', 2, 3, 2, 1, future_date_2, None),
                ('Task 3', None, 3, 1, 1, 2, future_date_1, '2024-01-12 10:00:00'),
                ('Task 4', 'Description 4', 1, 4, None, 2, future_date_3, None),
                ('Task 5', 'Description 5', 2, 2, 3, 3, future_date_2, None),
            ]
        )
        
        self.cursor.executemany(
            "INSERT INTO comments (task_id, user_id, content) VALUES (?, ?, ?)",
            [
                (1, 1, 'Comment 1'),
                (1, 2, 'Comment 2'),
                (2, 1, 'Comment 3'),
                (3, 2, 'Comment 4'),
            ]
        )
        
        self.conn.commit()
    
    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()
    
    def test_query_1_get_user_tasks(self):
        """Test getting all tasks for a specific user"""
        tasks = query_1_get_user_tasks(self.conn, 1)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0][1], 'Task 1')
    
    def test_query_2_get_tasks_by_status(self):
        """Test getting tasks by status"""
        tasks = query_2_get_tasks_by_status(self.conn, 'new')
        self.assertEqual(len(tasks), 2)
    
    def test_query_3_update_task_status(self):
        """Test updating task status"""
        query_3_update_task_status(self.conn, 1, 'in progress')
        self.cursor.execute("SELECT status_id FROM tasks WHERE id = 1")
        status_id = self.cursor.fetchone()[0]
        self.assertEqual(status_id, 2)
    
    def test_query_3_update_task_status_to_completed(self):
        """Test updating task status to completed sets completed_at"""
        query_3_update_task_status(self.conn, 1, 'completed')
        self.cursor.execute("SELECT completed_at FROM tasks WHERE id = 1")
        completed_at = self.cursor.fetchone()[0]
        self.assertIsNotNone(completed_at)
    
    def test_query_4_get_users_without_tasks(self):
        """Test getting users without tasks"""
        users = query_4_get_users_without_tasks(self.conn)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][1], 'Alice Brown')
    
    def test_query_5_add_new_task(self):
        """Test adding a new task"""
        # Use a future date to satisfy CHECK constraint
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        task_id = query_5_add_new_task(
            self.conn, 
            'New Task', 
            'New Description', 
            1, 
            'new', 
            'medium', 
            'development',
            future_date
        )
        self.assertIsNotNone(task_id)
        self.cursor.execute("SELECT title FROM tasks WHERE id = ?", (task_id,))
        title = self.cursor.fetchone()[0]
        self.assertEqual(title, 'New Task')
    
    def test_query_6_get_uncompleted_tasks(self):
        """Test getting uncompleted tasks"""
        tasks = query_6_get_uncompleted_tasks(self.conn)
        self.assertEqual(len(tasks), 4)
    
    def test_query_7_delete_task(self):
        """Test deleting a task"""
        query_7_delete_task(self.conn, 1)
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE id = 1")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)
    
    def test_query_7_delete_task_cascades_comments(self):
        """Test that deleting a task also deletes its comments"""
        # First verify comments exist
        self.cursor.execute("SELECT COUNT(*) FROM comments WHERE task_id = 1")
        initial_count = self.cursor.fetchone()[0]
        self.assertGreater(initial_count, 0)
        
        # Delete the task
        query_7_delete_task(self.conn, 1)
        
        # Verify comments are deleted
        self.cursor.execute("SELECT COUNT(*) FROM comments WHERE task_id = 1")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)
    
    def test_query_8_find_users_by_email(self):
        """Test finding users by email pattern"""
        users = query_8_find_users_by_email(self.conn, '%@gmail.com')
        self.assertEqual(len(users), 2)
    
    def test_query_9_update_user_name(self):
        """Test updating user name"""
        query_9_update_user_name(self.conn, 'New Name', 1)
        self.cursor.execute("SELECT fullname FROM users WHERE id = 1")
        name = self.cursor.fetchone()[0]
        self.assertEqual(name, 'New Name')
    
    def test_query_10_get_task_count_by_status(self):
        """Test getting task count by status"""
        counts = query_10_get_task_count_by_status(self.conn)
        self.assertEqual(len(counts), 5)
        # Check that 'new' status has 2 tasks
        new_count = [count for status, count in counts if status == 'new'][0]
        self.assertEqual(new_count, 2)
    
    def test_query_11_get_tasks_by_domain(self):
        """Test getting tasks by email domain"""
        tasks = query_11_get_tasks_by_domain(self.conn, '%@example.com')
        self.assertEqual(len(tasks), 3)
    
    def test_query_12_get_tasks_without_description(self):
        """Test getting tasks without description"""
        tasks = query_12_get_tasks_without_description(self.conn)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0][1], 'Task 3')
    
    def test_query_13_get_users_and_inprogress_tasks(self):
        """Test getting users and their in-progress tasks"""
        results = query_13_get_users_and_inprogress_tasks(self.conn)
        self.assertEqual(len(results), 2)
    
    def test_query_14_get_users_and_task_counts(self):
        """Test getting users and their task counts"""
        counts = query_14_get_users_and_task_counts(self.conn)
        self.assertEqual(len(counts), 4)
        # John Doe should have 2 tasks
        john_count = [count for name, count in counts if name == 'John Doe'][0]
        self.assertEqual(john_count, 2)
    
    def test_query_15_get_highest_priority_tasks(self):
        """Test getting highest priority tasks"""
        tasks = query_15_get_highest_priority_tasks(self.conn)
        self.assertEqual(len(tasks), 2)
        # Should be sorted by due date
        self.assertLessEqual(tasks[0][7], tasks[1][7])
    
    def test_query_16_get_overdue_tasks(self):
        """Test getting overdue tasks"""
        # Set a task's due date to past (but after created_at)
        # First, update created_at to an older date
        self.cursor.execute("UPDATE tasks SET created_at = '2020-01-01 00:00:00' WHERE id = 1")
        self.cursor.execute("UPDATE tasks SET due_date = '2020-01-15' WHERE id = 1")
        self.conn.commit()
        
        tasks = query_16_get_overdue_tasks(self.conn)
        self.assertGreaterEqual(len(tasks), 1)
    
    def test_query_17_get_task_statistics_by_category(self):
        """Test getting task statistics by category"""
        stats = query_17_get_task_statistics_by_category(self.conn)
        self.assertEqual(len(stats), 3)
        # Development category should have 2 tasks
        dev_count = [count for category, count in stats if category == 'development'][0]
        self.assertEqual(dev_count, 2)
    
    def test_query_18_get_latest_comments(self):
        """Test getting latest comments for a task"""
        comments = query_18_get_latest_comments(self.conn, 1, limit=2)
        self.assertEqual(len(comments), 2)
        # Should be ordered by created_at DESC
        self.assertGreaterEqual(comments[0][4], comments[1][4])
    
    def test_query_19_get_users_with_most_inprogress_tasks(self):
        """Test getting users with most in-progress tasks"""
        top_users = query_19_get_users_with_most_inprogress_tasks(self.conn, limit=2)
        self.assertEqual(len(top_users), 2)
        # Should be ordered by count DESC
        self.assertGreaterEqual(top_users[0][1], top_users[1][1])
    
    def test_query_20_get_average_completion_time(self):
        """Test getting average completion time"""
        # Update completed_at to be after created_at
        self.cursor.execute("UPDATE tasks SET completed_at = DATETIME(created_at, '+2 days') WHERE id = 3")
        self.conn.commit()
        
        avg_time = query_20_get_average_completion_time(self.conn)
        self.assertIsNotNone(avg_time)
        self.assertGreater(avg_time, 0)

if __name__ == '__main__':
    unittest.main()
