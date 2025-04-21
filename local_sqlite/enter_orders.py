from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from datetime import datetime
import sqlite3
import time

DB_FILE = "mealtracker.db"
console = Console()

def enter_orders():
    """Prompt for lunch and breakfast entree orders and save to the orders table."""
    try:
        console.clear()
        console.print(Panel("Enter Lunch & Breakfast Orders", title="Meal Tracker", style="bold magenta"))

        order_date = Prompt.ask("[cyan]Enter order date (YYYY-MM-DD)[/cyan]", default=datetime.now().strftime("%Y-%m-%d"))
        school_id = int(Prompt.ask("[cyan]Enter school ID[/cyan]", default="1"))

        lunch_input = Prompt.ask("[green]Lunch order (press Enter to skip)[/green]", default="")
        lunch_order = int(lunch_input) if lunch_input.strip().isdigit() else None

        breakfast_input = Prompt.ask("[blue]Breakfast order (press Enter to skip)[/blue]", default="")
        breakfast_order = int(breakfast_input) if breakfast_input.strip().isdigit() else None

        if lunch_order is None and breakfast_order is None:
            console.print("[yellow]⚠️ No data entered. Aborting.[/yellow]")
            return

        # Show confirmation table before committing to DB
        console.print("\n[bold magenta]Confirm Order Details[/bold magenta]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Field", style="dim")
        table.add_column("Value", style="bold")

        table.add_row("Order Date", order_date)
        table.add_row("School ID", str(school_id))
        table.add_row("Lunch Order", str(lunch_order) if lunch_order is not None else "—")
        table.add_row("Breakfast Order", str(breakfast_order) if breakfast_order is not None else "—")

        console.print(table)

        confirm = Confirm.ask("[green]✅ Add or update this order?[/green]", default=True)
        if not confirm:
            console.print("[yellow]❌ Operation cancelled.[/yellow]")
            return

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # Check for existing record
            cursor.execute("""
                SELECT * FROM orders WHERE order_date = ? AND school_id = ?
            """, (order_date, school_id))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE orders
                    SET lunch_order = COALESCE(?, lunch_order),
                        breakfast_order = COALESCE(?, breakfast_order)
                    WHERE order_date = ? AND school_id = ?
                """, (lunch_order, breakfast_order, order_date, school_id))
                console.print(f"[green]✅ Order updated for {order_date} (School ID: {school_id})[/green]")
            else:
                cursor.execute("""
                    INSERT INTO orders (order_date, lunch_order, breakfast_order, school_id)
                    VALUES (?, ?, ?, ?)
                """, (order_date, lunch_order, breakfast_order, school_id))
                console.print(f"[green]✅ Order added for {order_date} (School ID: {school_id})[/green]")

            conn.commit()
            time.sleep(1.5)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        time.sleep(2)

# Run the function
if __name__ == "__main__":
    enter_orders()
