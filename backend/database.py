import sqlite3

DB_NAME = "app.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'low',
            status TEXT DEFAULT 'pending',
            due_date TEXT,
            owner_email TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_user(name: str, email: str, hashed_password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (name, email, hashed_password)
        VALUES (?, ?, ?)
        """,
        (name, email, hashed_password)
    )

    conn.commit()
    conn.close()


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    return dict(user) if user else None


def create_task(title, description, priority, due_date, owner_email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (
            title,
            description,
            priority,
            due_date,
            owner_email
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, description, priority, due_date, owner_email)
    )

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return task_id


def get_task_by_id(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    task = cursor.fetchone()
    conn.close()

    return dict(task) if task else None


def get_filtered_tasks(owner_email: str, status: str = None, priority: str = None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE owner_email = ?"
    values = [owner_email]

    if status:
        query += " AND status = ?"
        values.append(status)

    if priority:
        query += " AND priority = ?"
        values.append(priority)

    query += " ORDER BY id DESC"

    cursor.execute(query, values)
    tasks = cursor.fetchall()

    conn.close()

    return [dict(task) for task in tasks]


def update_task(task_id: int, title: str, description: str, priority: str, due_date: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, priority = ?, due_date = ?
        WHERE id = ?
        """,
        (title, description, priority, due_date, task_id)
    )

    conn.commit()
    conn.close()


def update_task_status(task_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        """,
        (status, task_id)
    )

    conn.commit()
    conn.close()


def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    conn.commit()
    conn.close()


def get_task_summary(owner_email: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status, COUNT(*) as count
        FROM tasks
        WHERE owner_email = ?
        GROUP BY status
        """,
        (owner_email,)
    )

    rows = cursor.fetchall()
    conn.close()

    summary = {
        "total": 0,
        "pending": 0,
        "in_progress": 0,
        "done": 0
    }

    for row in rows:
        status = row["status"]
        count = row["count"]

        summary["total"] += count

        if status == "pending":
            summary["pending"] = count
        elif status == "in-progress":
            summary["in_progress"] = count
        elif status == "done":
            summary["done"] = count

    return summary