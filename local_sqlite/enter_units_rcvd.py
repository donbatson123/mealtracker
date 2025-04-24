import sqlite3
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
import os

# Constants
DB_FILE = "mealtracker.db"
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def get_items():
    """Fetch items from sorted_items table."""
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query("SELECT itemid, itemname FROM sorted_items", conn)

def enter_units_rcvd_data():
    df_sorted = get_items()
    serve_date = datetime.now().strftime('%Y-%m-%d')
    clear_screen()

    console.print(Panel.fit(
        f"[bold green]📅 Serve Date:[/bold green] {serve_date}",
        title="MealTracker - Units Received Entry",
        border_style="cyan"
    ))

    records = []
    console.print("\n[bold blue]➡️ Enter data for each item[/bold blue] (Enter for 0, or 'q' to quit):\n")

    for _, row in df_sorted.iterrows():
        itemid = row['itemid']
        itemname = row['itemname']
        console.rule(f"[bold yellow]{itemname}[/bold yellow]")

        units_received = Prompt.ask("  Units Received", default="0")
        if units_received.lower() == 'q':
            console.print("  ↪️ [italic]Quitting item entry early...[/italic]")
            break
        try:
            units_received = float(units_received)
        except ValueError:
            console.print("  [red]⚠️ Invalid input. Skipping item.[/red]")
            continue

        temp_rcvd = Prompt.ask("  Received Temp (°F)", default="", show_default=False)
        if temp_rcvd.lower() == 'q':
            console.print("  ↪️ [italic]Quitting item entry early...[/italic]")
            break
        elif temp_rcvd == '':
            temp_rcvd = None
        else:
            try:
                temp_rcvd = float(temp_rcvd)
            except ValueError:
                console.print("  [red]⚠️ Invalid input. Skipping item.[/red]")
                continue

        records.append({
            'itemid': itemid,
            'itemname': itemname,
            'units_received': units_received,
            'temp_rcvd': temp_rcvd,
        })

    if not records:
        console.print("\n[red]⚠️ No data to save. Exiting.[/red]")
        return

    time_rcvd = Prompt.ask("\n⏰ Enter time received (HH:MM)")
    try:
        datetime.strptime(time_rcvd, "%H:%M")
    except ValueError:
        console.print("[red]❌ Invalid time format. Aborting.[/red]")
        return

    # Review entries
    table = Table(title="📝 Review Entered Data", box=None, show_lines=True)
    table.add_column("Index", style="dim")
    table.add_column("Item Name")
    table.add_column("Units Received")
    table.add_column("Temp Received (°F)", justify="right")

    for idx, rec in enumerate(records):
        table.add_row(
            str(idx),
            rec["itemname"],
            str(rec["units_received"]),
            str(rec["temp_rcvd"]) if rec["temp_rcvd"] is not None else "-"
        )

    console.print("\n", table)

    # Edit entries if needed
    if Confirm.ask("✏️ Would you like to edit any entries?", default=False):
        while True:
            index_to_edit = Prompt.ask("Enter index to edit (or blank to finish)", default="", show_default=False)
            if index_to_edit == "":
                break
            try:
                idx = int(index_to_edit)
                rec = records[idx]
                console.print(f"\nEditing: [bold]{rec['itemname']}[/bold]")

                units_received = Prompt.ask("  New Units Received", default=str(rec["units_received"]))
                temp_rcvd = Prompt.ask("  New Temp (°F)", default=str(rec["temp_rcvd"]) if rec["temp_rcvd"] else "")

                rec["units_received"] = float(units_received)
                rec["temp_rcvd"] = float(temp_rcvd) if temp_rcvd != "" else None

                records[idx] = rec
                console.print("[green]✔ Entry updated.[/green]\n")
            except (ValueError, IndexError):
                console.print("[red]❌ Invalid index. Try again.[/red]")

    # Export to Excel
    df_export = pd.DataFrame.from_records(records)
    df_export["serve_date"] = serve_date
    df_export["time_rcvd"] = time_rcvd
    filename_base = f"{EXPORT_FOLDER}/saladbar_rcvd_{serve_date.replace('-', '')}"
    export_path = f"{filename_base}.xlsx"
    df_export.to_excel(export_path, index=False)
    console.print(f"\n📁 [bold]Data exported to:[/bold] [green]{export_path}[/green]")

    if not Confirm.ask("💾 Save to database now?", default=True):
        console.print("[yellow]⚠️ Data was not saved to database.[/yellow]")
        return

    # Insert or update database records
    with sqlite3.connect(DB_FILE) as conn:
        for rec in records:
            cursor = conn.execute(
                "SELECT 1 FROM salad_bar WHERE itemid = ? AND serve_date = ?",
                (rec['itemid'], serve_date)
            )
            exists = cursor.fetchone()

            if exists:
                conn.execute(
                    """
                    UPDATE salad_bar
                    SET time_rcvd = ?, temp_rcvd = ?, units_received = ?
                    WHERE itemid = ? AND serve_date = ?
                    """,
                    (
                        time_rcvd,
                        rec['temp_rcvd'],
                        rec['units_received'],
                        rec['itemid'],
                        serve_date
                    )
                )
                console.print(f"[yellow]🔄 Updated:[/yellow] {rec['itemname']}")
            else:
                conn.execute(
                    """
                    INSERT INTO salad_bar (
                        itemid, serve_date, time_rcvd, temp_rcvd,
                        units_received, culled, ending_inv, leftovers,
                        current_inv, units_used, portions_prepared, total_served,
                        time_served, temp_served, synced
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rec['itemid'], serve_date, time_rcvd, rec['temp_rcvd'],
                        rec['units_received'], 0, 0, 0,
                        0, 0, 0, 0,
                        "", 0.0, 0
                    )
                )
                console.print(f"[green]➕ Inserted:[/green] {rec['itemname']}")

    console.print(f"\n[bold green]✅ {len(records)} salad bar records inserted successfully.[/bold green]")

# Run the function
if __name__ == "__main__":
    enter_units_rcvd_data()
