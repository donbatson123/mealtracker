
import sqlite3
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor
from rich.console import Console

console = Console()

sqlite_db_path = "mealtracker.db"
pg_db_params = {
    'dbname': 'your_database',
    'user': 'user_name',
    'password': 'secure_password',
    'host': 'your_host',
    'port': 5432
}

# Optional helper to clear screen
def clear_screen():
    import os
    os.system("cls" if os.name == "nt" else "clear")

def sync_students_from_postgres():
    clear_screen()
    try:
        with psycopg2.connect(**pg_db_params) as pg_conn:
            with pg_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT perm_id, first_name, last_name, staff, school FROM students")
                students_pg = pd.DataFrame(cursor.fetchall())
        console.print(f"[green]✅ Pulled {len(students_pg)} students from PostgreSQL[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error fetching from PostgreSQL: {e}[/red]")
        return

    if students_pg.empty:
        console.print("[yellow]⚠️ No students found in PostgreSQL[/yellow]")
        return

    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            # Ensure local table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    perm_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    staff TEXT,
                    school TEXT
                )
            """)
            conn.commit()

            existing_ids = pd.read_sql_query("SELECT perm_id FROM students", conn)['perm_id'].tolist()
    except Exception as e:
        console.print(f"[red]❌ Error checking local students: {e}[/red]")
        return

    new_students = students_pg[~students_pg['perm_id'].isin(existing_ids)]

    if new_students.empty:
        console.print("[blue]ℹ️ No new students to insert[/blue]")
        return

    try:
        with sqlite3.connect(sqlite_db_path) as conn:
            new_students.to_sql('students', conn, if_exists='append', index=False)
        console.print(f"[green]✅ Inserted {len(new_students)} new students into SQLite[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to insert into SQLite: {e}[/red]")


# Run the function
if __name__ == "__main__":
    sync_students_from_postgres()