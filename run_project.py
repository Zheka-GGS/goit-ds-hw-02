# -*- coding: utf-8 -*- 
# Цей файл відповідає за демонстрацію роботи проекту. Він послідовно виконує всі необхідні кроки: створення таблиць, заповнення бази даних випадковими даними, тестування SQL-запитів та виведення інформації про базу даних.
import os
import subprocess
import sys
import sqlite3
# Встановлення шляху до бази даних через змінну середовища DB_PATH = os.getenv('DB_PATH', 'task_management.db')
DB_PATH = os.getenv('DB_PATH', 'task_management.db')
# Функція для виконання SQL-скриптів, яка читає SQL-команди з файлу та виконує їх по черзі, обробляючи можливі помилки.
def run_sql_script(script_path):
    """Execute SQL script"""
    print(f"Executing {script_path}...")
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_commands = f.read()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Split commands and execute them
    commands = sql_commands.split(';')
    for command in commands:
        command = command.strip()
        if command:
            try:
                cursor.execute(command)
            except sqlite3.Error as e:
                print(f"SQL execution error: {e}")
                print(f"Command: {command}")
    
    conn.commit()
    conn.close()
    print(f"[SUCCESS] {script_path} executed successfully")
# Функція для виконання Python-скриптів, яка запускає інший Python-файл як підпроцес, передаючи йому шлях до бази даних через змінну середовища. Вона також обробляє вивід та помилки.
def run_python_script(script_path):
    """Execute Python script"""
    print(f"Executing {script_path}...")
    # Pass the database path as an environment variable to the subprocess
    env = os.environ.copy()
    env['DB_PATH'] = DB_PATH
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, env=env)
    
    if result.returncode != 0:
        print(f"Error executing {script_path}:")
        print(result.stderr)
    else:
        print(f"[SUCCESS] {script_path} executed successfully")
        if result.stdout:
            print("Output:", result.stdout[:500])  # Limit output for readability
# Головна функція для запуску процесу демонстрації. Вона послідовно виконує всі кроки, виводячи інформацію про кожен етап та результати виконання.
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
    
    # Step 3: Test all queries
    print("Step 3: Testing all SQL queries")
    run_python_script('test_queries.py')
    print()
    
    # Step 4: Display database information
    print("Step 4: Database information")
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
    
    # Print all statuses
    cursor.execute("SELECT * FROM status")
    statuses = cursor.fetchall()
    print("Statuses:", statuses)
    
    conn.close()
    
    print("\n=== Demonstration completed ===")
    print("Project contains:")
    print("- create_tables.sql: Creating database tables")
    print("- seed.py: Populating database with random data")
    print("- queries.sql: All required SQL queries")
    print("- test_queries.py: Testing all queries")
    print("- README.md: Project documentation")
    print("- requirements.txt: Project dependencies")

if __name__ == "__main__":
    main()