import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse
import psycopg2
from rich.console import Console
from rich.table import Table
import sys
import os

# Database connection config
DB_CONFIG = {
    "host": "your_host",
    "database": "your_database",
    "user": "user_name",
    "password": "secure_password",
    "port": 5432
}

EXPORT_DIR = Path("admin_exports")
EXPORT_DIR.mkdir(exist_ok=True)

console = Console()
EXPECTED_COLUMNS = {"Perm ID", "Student Name", "Staff Name"}


def clean_and_reorder(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and reorder the student DataFrame."""
    df.rename(columns={"Perm ID": "perm_id", "Staff Name": "staff"}, inplace=True)
    df["school"] = ""

    df[["last_name_staff", "first_name_staff", *_]] = df["staff"].str.split(",", expand=True)
    df["staff"] = df["last_name_staff"]

    df[["last_name", "first_name", *_]] = df["Student Name"].str.split(",", expand=True)
    df["first_name"] = df["first_name"].str.split(" ").str[0]

    df.drop(columns=["Student Name", "Ed-Fi ID", "SSID", "Last Name", "last_name_staff", "first_name_staff"], inplace=True, errors="ignore")
    df = df[["perm_id", "first_name", "last_name", "staff", "school"]]
    return df


def validate_columns(df: pd.DataFrame, source_name: str):
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        sys.exit(f"❌ ERROR: Missing expected columns in {source_name}: {', '.join(missing)}")


def get_existing_perm_ids() -> set:
    """Retrieve existing perm_id values from the database."""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT perm_id FROM students;")
                return {row[0] for row in cur.fetchall()}
    except Exception as e:
        sys.exit(f"❌ Could not fetch existing perm_ids: {e}")


def insert_into_postgres(df: pd.DataFrame) -> list:
    """Insert cleaned DataFrame into PostgreSQL and return inserted rows."""
    existing_ids = get_existing_perm_ids()
    df_new = df[~df["perm_id"].isin(existing_ids)]

    if df_new.empty:
        console.print("[bold yellow]⚠️ No new students to insert. All perm_ids already exist.[/bold yellow]")
        return []

    inserted_rows = []
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for _, row in df_new.iterrows():
                    cur.execute("""
                        INSERT INTO students (perm_id, first_name, last_name, staff, school)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING perm_id, first_name, last_name, staff, school
                    """, tuple(row))
                    inserted_rows.append(cur.fetchone())
        return inserted_rows
    except Exception as e:
        sys.exit(f"❌ Database insert error: {e}")



def display_rich_table(data: list):
    table = Table(title="📋 Newly Inserted Students", header_style="bold magenta")
    table.add_column("perm_id", style="cyan", justify="right")
    table.add_column("First Name", style="green")
    table.add_column("Last Name", style="green")
    table.add_column("Staff", style="yellow")
    table.add_column("School", style="blue")

    for row in data:
        table.add_row(*[str(x) for x in row])

    console.print(table)


def main(file1: str, file2: str):
    file1 = Path(file1)
    file2 = Path(file2)
    #file1 = "StudentsRSE03.csv"
    #file2 = "StudentsWRS03.csv"

    if not file1.exists() or not file2.exists():
        sys.exit("❌ ERROR: One or both input files do not exist.")

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    validate_columns(df1, file1.name)
    validate_columns(df2, file2.name)

    df1 = clean_and_reorder(df1)
    df2 = clean_and_reorder(df2)

    combined_df = pd.concat([df1, df2], ignore_index=True)
    console.print(f"[cyan]📥 {len(combined_df)} total student records prepared for insert.[/cyan]")

    # Export to Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = EXPORT_DIR / f"students_export_{timestamp}.xlsx"
    combined_df.to_excel(export_path, index=False)
    console.print(f"[green]📁 Exported cleaned data to:[/green] {export_path}")

    # Insert and display
    inserted = insert_into_postgres(combined_df)
    if inserted:
        display_rich_table(inserted)
    else:
        console.print("[yellow]No new data inserted.[/yellow]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and insert student CSVs into PostgreSQL.")
    parser.add_argument("file1", help="First CSV file (e.g., StudentsWRS03.csv)")
    parser.add_argument("file2", help="Second CSV file (e.g., StudentsRSE03.csv)")
    args = parser.parse_args()
    main(args.file1, args.file2)
