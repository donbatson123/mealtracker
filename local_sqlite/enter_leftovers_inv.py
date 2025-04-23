import sqlite3
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.prompt import FloatPrompt, Confirm
from pathlib import Path

DB_FILE = "mealtracker.db"
EXPORT_FOLDER = "exports"
console = Console()

def clear_screen():
    import os
    os.system("cls" if os.name == "nt" else "clear")


def get_items():
    with sqlite3.connect(DB_FILE) as conn:
        return pd.read_sql_query("SELECT itemid, itemname FROM sorted_items", conn)


def enter_leftovers_and_ending_inv():
    df_sorted = get_items()
    clear_screen()

    serve_date = Prompt.ask("📅 Enter serve date", default=datetime.now().strftime('%Y-%m-%d'))
    if serve_date.lower() == 'q':
        console.print("\n👋 Quit requested. Exiting...", style="bold yellow")
        return

    time_served = Prompt.ask("⏰ Enter time served (HH:MM)", default="11:30")
    if time_served.lower() == 'q':
        console.print("\n👋 Quit requested. Exiting...", style="bold yellow")
        return

    records = []
    clear_screen()

    console.print("\n➡️ Enter leftovers and ending inventory for each item (type [bold]'q'[/bold] to quit early):\n", style="bold green")

    for _, row in df_sorted.iterrows():
        itemid = row["itemid"]
        itemname = row["itemname"]
        console.print(f"\n[item]{itemname}[/item]")

        leftovers_input = Prompt.ask("  🍽 Leftovers (or 'q' to quit)", default="0")
        if leftovers_input.lower() == 'q':
            console.print("\n👋 Quit requested. Exiting item entry...", style="bold yellow")
            break

        ending_input = Prompt.ask("  📦 Ending Inventory (or 'q' to quit)", default="0")
        if ending_input.lower() == 'q':
            console.print("\n👋 Quit requested. Exiting item entry...", style="bold yellow")
            break

        try:
            leftovers = float(leftovers_input)
            ending_inv = float(ending_input)
        except ValueError:
            console.print("⚠️ Invalid input. Please enter a number or 'q'. Skipping item.", style="bold red")
            continue

        records.append({
            "itemid": itemid,
            "itemname": itemname,
            "leftovers": leftovers,
            "ending_inv": ending_inv
        })

    if not records:
        console.print("\n⚠️ No data entered. Aborting.", style="bold red")
        return

    # ✅ Preview table
    table = Table(title="Leftovers & Ending Inventory", show_lines=True)
    table.add_column("Item", style="cyan")
    table.add_column("Leftovers", justify="right")
    table.add_column("Ending Inv", justify="right")

    for rec in records:
        table.add_row(rec["itemname"], str(rec["leftovers"]), str(rec["ending_inv"]))

    console.print("\n📋 Preview of Data:\n")
    console.print(table)

    # 💾 Export to Excel
    df_export = pd.DataFrame.from_records(records)
    df_export["serve_date"] = serve_date
    df_export["time_served"] = time_served

    Path(EXPORT_FOLDER).mkdir(exist_ok=True)
    filename = f"{EXPORT_FOLDER}/leftovers_endinginv_{serve_date.replace('-', '')}.xlsx"
    df_export.to_excel(filename, index=False)
    console.print(f"\n🧾 Data exported to [bold]{filename}[/bold]")

    # ✅ Confirm before DB insert
    if Confirm.ask("\n✅ Save this data to the database?"):
        with sqlite3.connect(DB_FILE) as conn:
            for rec in records:
                conn.execute(
                    """
                    INSERT INTO salad_bar (
                        itemid, serve_date, units_received, leftovers, ending_inv, time_served
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rec["itemid"], serve_date,
                        rec.get("units_received", 0),  # 👈 fallback to 0 if not present
                        rec["leftovers"], rec["ending_inv"], time_served
                    )
                )
        console.print(f"\n✅ {len(records)} records saved to salad_bar table.")

# Run the function
if __name__ == "__main__":
    enter_leftovers_and_ending_inv()