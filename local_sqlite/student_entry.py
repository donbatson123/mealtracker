import sqlite3
import time
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

# Optional helper to clear screen
def clear_screen():
    import os
    os.system("cls" if os.name == "nt" else "clear")

console = Console()

def add_students(db_file: str = "mealtracker.db", clear_fn=clear_screen):
    """Insert a new student into the students table."""

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        if clear_fn:
            clear_fn()

        console.print(Panel("Add New Student", title="Meal Tracker", style="bold cyan"))

        perm_id = Prompt.ask("[cyan]Enter student ID (perm_id)[/cyan]").strip()
        first_name = Prompt.ask("[cyan]Enter first name[/cyan]").strip()
        last_name = Prompt.ask("[cyan]Enter last name[/cyan]").strip()
        staff = Prompt.ask("[cyan]Enter staff name[/cyan]").strip().lower()

        if not all([perm_id, first_name, last_name, staff]):
            console.print("[bold red]All fields are required. Student not added.[/bold red]")
            return

        # Show confirmation table
        table = Table(title="Confirm Student Information", show_header=True, header_style="bold magenta")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Student ID", perm_id)
        table.add_row("First Name", first_name)
        table.add_row("Last Name", last_name)
        table.add_row("Staff", staff)

        console.print("\n")
        console.print(table)

        if not Confirm.ask("\n✅ Add this student?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        # Insert into DB
        cursor.execute("""
            INSERT INTO students (perm_id, first_name, last_name, staff)
            VALUES (?, ?, ?, ?);
        """, (perm_id, first_name, last_name, staff))
        conn.commit()

        success = Text(f"✅ Student {first_name} {last_name} added successfully!", style="bold green")
        console.print(success)
        time.sleep(1)

    except sqlite3.Error as e:
        console.print(Text(f"❌ Error inserting student: {e}", style="bold red"))
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

# Run the function
if __name__ == "__main__":
    add_students()
