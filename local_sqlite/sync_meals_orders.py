def sync_meals_orders(dry_run=False):
    """Sync unsynced meals, orders, and salad_bar data from SQLite to PostgreSQL."""
    import sqlite3
    import psycopg2
    import pandas as pd
    from psycopg2.extras import execute_values
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from dotenv import load_dotenv
    import os

    # Load .env from the current directory
    load_dotenv()

    console = Console()
    sqlite_db_path = 'mealtracker.db'

    # PostgreSQL connection details
    pg_db_params  = {
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PG_PORT", 5432)),
    "dbname": os.getenv("PG_DBNAME"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD")
    }

    # Tables to sync and which columns to exclude from sync
    tables_to_transfer = {
        "meals": ["id"],
        "orders": ["id", "school_id"],
        "salad_bar": ["salad_bar_id"]  # newly added
    }

    def fetch_unsynced_data(db_path, table, exclude_columns=None):
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall() if col[1] not in (exclude_columns or [])]
                query = f"SELECT {', '.join(columns)} FROM {table} WHERE synced = 0"
                df = pd.read_sql_query(query, conn)
                
                # Clean NaNs and invalid time strings
                df.replace({"": None, "NaN": None}, inplace=True)
                if "time" in df.columns:
                    df["time"] = df["time"].apply(lambda x: x if x and str(x).strip() not in ("", "NaN") else None)
                print(df)
                return df
        except Exception as e:
            console.print(f"[red]❌ Failed to fetch from {table}: {e}[/red]")
            return pd.DataFrame()

    def insert_postgresql_data(df, pg_params, table, conflict_column=None):
        if df.empty:
            console.print(f"[yellow]⚠️ No unsynced data in {table}[/yellow]")
            return False
        if dry_run:
            console.print(f"[blue]💡 Dry run: Skipping insert for {table} ({len(df)} rows)[/blue]")
            return True
        try:
            with psycopg2.connect(**pg_params) as conn:
                with conn.cursor() as cursor:
                    columns = df.columns.tolist()
                    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s"
                    if conflict_column:
                        query += f" ON CONFLICT ({conflict_column}) DO NOTHING"
                    data = [tuple(row) for row in df.values]
                    execute_values(cursor, query, data)
                    conn.commit()
            console.print(f"[green]✅ Inserted {len(df)} rows into {table}[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ PostgreSQL insert error for {table}: {e}[/red]")
            return False

    def update_sqlite_synced_flag(db_path, table):
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(f"UPDATE {table} SET synced = 1 WHERE synced = 0")
                conn.commit()
            console.print(f"[green]✅ Marked synced in {table}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to update synced flag in {table}: {e}[/red]")

    # Begin sync
    console.print(Panel("🔄 Syncing Meals, Orders & Salad Bar", style="bold magenta"))

    for table, exclude in tables_to_transfer.items():
        console.print(f"\n[bold cyan]Processing table:[/bold cyan] {table}")
        df = fetch_unsynced_data(sqlite_db_path, table, exclude_columns=exclude)
        if not df.empty:
            synced = insert_postgresql_data(df, pg_db_params, table)
            if synced:
                update_sqlite_synced_flag(sqlite_db_path, table)

    console.print("\n[bold green]🎉 Sync complete![/bold green]")


# Run the function
if __name__ == "__main__":
    sync_meals_orders(dry_run=False)
