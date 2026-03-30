# -*- coding: utf-8 -*- 
import os
import subprocess
import sys
import sqlite3
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

# Database path
DB_PATH = os.getenv('DB_PATH', 'task_management.db')

def run_sql_script(script_path):
    """Execute SQL script"""
    if not os.path.exists(script_path):
        print(f"Error: File {script_path} not found")
        return
    
    print(f"Executing {script_path}...")
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_commands = f.read()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.executescript(sql_commands)
        print(f"[SUCCESS] {script_path} executed successfully")
    except sqlite3.Error as e:
        print(f"SQL execution error: {e}")
    finally:
        conn.close()

def run_python_script(script_path):
    """Execute Python script"""
    print(f"Executing {script_path}...")
    env = os.environ.copy()
    env['DB_PATH'] = DB_PATH
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, env=env)
    
    if result.returncode != 0:
        print(f"Error executing {script_path}:")
        print(result.stderr)
    else:
        print(f"[SUCCESS] {script_path} executed successfully")
        if result.stdout:
            print("Output:", result.stdout[:500])

def display_results(title, results, max_items=5):
    """Display query results in a formatted way"""
    print(f"\n{title}")
    if not results:
        print("  No results found")
        return
    
    for i, item in enumerate(results[:max_items]):
        print(f"  {i+1}. {item}")
    
    if len(results) > max_items:
        print(f"  ... and {len(results) - max_items} more")

def main():
    print("=== Task Management System Project Demonstration ===\n")
    
    # Step 1: Create database tables
    print("Step 1: Creating database tables")
    run_sql_script('create_tables.sql')
    print()
    
    # Step 2: Populate database
    print("Step 2: Populating database with random data")
    run_python_script('seed.py')
    print()
    
    # Step 3: Execute all queries
    print("Step 3: Testing all SQL queries")
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Query 1: Get all tasks for a specific user
        print("\n1. Tasks for user with ID 1:")
        tasks = query_1_get_user_tasks(conn, 1)
        for task in tasks[:5]:
            print(f"  Task: {task}")
        
        # Query 2: Get tasks by status
        print("\n2. Tasks with status 'new':")
        new_tasks = query_2_get_tasks_by_status(conn, 'new')
        for task in new_tasks[:5]:
            print(f"  Task: {task}")
        
        # Query 3: Update task status
        print("\n3. Updating task status:")
        if tasks:
            task_id = tasks[0][0]
            print(f"  Updating task {task_id} to 'in progress'")
            query_3_update_task_status(conn, task_id, 'in progress')
            print(f"  Task {task_id} updated successfully")
        
        # Query 4: Get users without tasks
        print("\n4. Users without tasks:")
        users_no_tasks = query_4_get_users_without_tasks(conn)
        for user in users_no_tasks:
            print(f"  User: {user}")
        
        # Query 5: Add new task
        print("\n5. Adding new task:")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()[0]
        print(f"  Adding new task for user {user_id}")
        new_task_id = query_5_add_new_task(conn, "Test Task", "This is a test task description", user_id)
        print(f"  New task added successfully with ID {new_task_id}")
        
        # Query 6: Get uncompleted tasks
        print("\n6. Uncompleted tasks:")
        uncompleted = query_6_get_uncompleted_tasks(conn)
        for task in uncompleted[:5]:
            print(f"  Task: {task}")
        
        # Query 7: Delete task
        print("\n7. Deleting a task:")
        if tasks and len(tasks) > 0:
            task_id = tasks[-1][0]
            print(f"  Deleting task {task_id}")
            query_7_delete_task(conn, task_id)
            print(f"  Task {task_id} deleted successfully")
        else:
            print("  No tasks available to delete")
        
        # Query 8: Find users by email pattern
        print("\n8. Users with gmail addresses:")
        gmail_users = query_8_find_users_by_email(conn, '%@gmail.com')
        for user in gmail_users[:5]:
            print(f"  User: {user}")
        
        # Query 9: Update user name
        print("\n9. Updating user name:")
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()[0]
        print(f"  Updating name for user {user_id}")
        query_9_update_user_name(conn, "Updated Name", user_id)
        print(f"  User {user_id} name updated successfully")
        
        # Query 10: Get task count by status
        print("\n10. Task count by status:")
        counts = query_10_get_task_count_by_status(conn)
        for status, count in counts:
            print(f"  {status}: {count}")
        
        # Query 11: Get tasks by domain
        print("\n11. Tasks assigned to users with 'example.com' domain:")
        domain_tasks = query_11_get_tasks_by_domain(conn, '%@example.com')
        for task in domain_tasks[:5]:
            print(f"  Task: {task}")
        
        # Query 12: Get tasks without description
        print("\n12. Tasks without description:")
        no_desc_tasks = query_12_get_tasks_without_description(conn)
        for task in no_desc_tasks[:5]:
            print(f"  Task: {task}")
        
        # Query 13: Get users and their in-progress tasks
        print("\n13. Users and their in-progress tasks:")
        in_progress = query_13_get_users_and_inprogress_tasks(conn)
        for item in in_progress[:5]:
            print(f"  {item}")
        
        # Query 14: Get users and their task counts
        print("\n14. Users and their task counts:")
        user_counts = query_14_get_users_and_task_counts(conn)
        for user, count in user_counts[:10]:
            print(f"  {user}: {count} tasks")
        
        # Query 15: Get highest priority tasks
        print("\n15. Tasks with highest priority:")
        high_priority = query_15_get_highest_priority_tasks(conn)
        for task in high_priority[:5]:
            print(f"  Task: {task}")
        
        # Query 16: Get overdue tasks
        print("\n16. Overdue tasks:")
        overdue = query_16_get_overdue_tasks(conn)
        for task in overdue[:5]:
            print(f"  Task: {task}")
        
        # Query 17: Get task statistics by category
        print("\n17. Task statistics by category:")
        category_stats = query_17_get_task_statistics_by_category(conn)
        for category, count in category_stats:
            print(f"  {category}: {count} tasks")
        
        # Query 18: Get latest comments for a task
        print("\n18. Latest comments for task with ID 1:")
        cursor.execute("SELECT id FROM tasks LIMIT 1")
        task_id = cursor.fetchone()[0]
        comments = query_18_get_latest_comments(conn, task_id)
        for comment in comments:
            print(f"  Comment: {comment}")
        
        # Query 19: Get users with most in-progress tasks
        print("\n19. Users with most in-progress tasks:")
        top_users = query_19_get_users_with_most_inprogress_tasks(conn)
        for user, count in top_users:
            print(f"  {user}: {count} tasks")
        
        # Query 20: Get average completion time
        print("\n20. Average task completion time:")
        avg_time = query_20_get_average_completion_time(conn)
        print(f"  Average: {avg_time:.2f} days")
        
    except Exception as e:
        print(f"Error executing queries: {e}")
    finally:
        conn.close()
    
    # Step 4: Display database information
    print("\nStep 4: Database information")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Number of users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Number of users: {user_count}")
    
    # Number of tasks
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    print(f"Number of tasks: {task_count}")
    
    # Number of statuses
    cursor.execute("SELECT COUNT(*) FROM status")
    status_count = cursor.fetchone()[0]
    print(f"Number of statuses: {status_count}")
    
    # Number of priorities
    cursor.execute("SELECT COUNT(*) FROM priority")
    priority_count = cursor.fetchone()[0]
    print(f"Number of priorities: {priority_count}")
    
    # Number of categories
    cursor.execute("SELECT COUNT(*) FROM category")
    category_count = cursor.fetchone()[0]
    print(f"Number of categories: {category_count}")
    
    # Number of comments
    cursor.execute("SELECT COUNT(*) FROM comments")
    comment_count = cursor.fetchone()[0]
    print(f"Number of comments: {comment_count}")
    
    conn.close()
    
    print("\n=== Demonstration completed ===")
    print("Project contains:")
    print("- create_tables.sql: Creating database tables")
    print("- seed.py: Populating database with random data")
    print("- queries.py: All required SQL queries (20 functions)")
    print("- run_project.py: Demonstration of all queries")
    print("- test_queries.py: Unit tests for all queries")
    print("- README.md: Project documentation")
    print("- requirements.txt: Project dependencies")

if __name__ == "__main__":
    main()
