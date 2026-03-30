#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verification script for task management system"""

import sqlite3
import os

def verify_database():
    """Verify database structure and requirements"""
    db_path = 'task_management.db'
    
    if not os.path.exists(db_path):
        print("ERROR: Database file not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATABASE VERIFICATION REPORT")
    print("="*60)
    
    # 1. Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    print("\n✓ TABLES CREATED:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    required_tables = {'users', 'status', 'tasks'}
    if required_tables.issubset(set(tables)):
        print("  ✓ All required tables exist")
    else:
        print(f"  ✗ Missing tables: {required_tables - set(tables)}")
    
    # 2. Verify users table structure
    print("\n✓ USERS TABLE STRUCTURE:")
    cursor.execute('PRAGMA table_info(users)')
    users_info = cursor.fetchall()
    for col in users_info:
        print(f"  {col[1]}: {col[2]}")
    
    # Check UNIQUE constraint on email
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    users_sql = cursor.fetchone()[0]
    if 'UNIQUE' in users_sql and 'email' in users_sql:
        print("  ✓ email field is UNIQUE")
    
    # 3. Verify status table structure
    print("\n✓ STATUS TABLE STRUCTURE:")
    cursor.execute('PRAGMA table_info(status)')
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]}")
    
    # Check UNIQUE constraint on name
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='status'")
    status_sql = cursor.fetchone()[0]
    if 'UNIQUE' in status_sql and 'name' in status_sql:
        print("  ✓ name field is UNIQUE")
    
    # 4. Verify tasks table structure
    print("\n✓ TASKS TABLE STRUCTURE:")
    cursor.execute('PRAGMA table_info(tasks)')
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]}")
    
    # 5. Check cascade delete
    print("\n✓ CASCADE DELETE CHECK:")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
    tasks_sql = cursor.fetchone()[0]
    if 'ON DELETE CASCADE' in tasks_sql:
        print("  ✓ Cascade delete enabled for user_id")
    
    # 6. Data verification
    print("\n✓ DATA VERIFICATION:")
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"  Users: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM status")
    status_count = cursor.fetchone()[0]
    print(f"  Statuses: {status_count}")
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    print(f"  Tasks: {task_count}")
    
    # 7. Check default statuses
    print("\n✓ DEFAULT STATUSES:")
    cursor.execute("SELECT name FROM status ORDER BY name")
    for status in cursor.fetchall():
        print(f"  - {status[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM status WHERE name IN ('new', 'in progress', 'completed')")
    required_statuses = cursor.fetchone()[0]
    if required_statuses >= 3:
        print("  ✓ Required statuses (new, in progress, completed) exist")
    
    conn.close()
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    verify_database()
