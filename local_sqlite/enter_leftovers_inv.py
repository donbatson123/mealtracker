import sqlite3
import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.prompt import FloatPrompt, Confirm
from pathlib import Path
from utils import upsert_salad_bar

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

    serve_date = Prompt.ask("\U0001F4C5 Enter serve date", default=datetime.now().strftime('%Y-%m-%d'))
    if serve_date.lower() == 'q':
        console.print("\n\U0001F44B Quit requested. Exiting...", style="bold yellow")
        return

    time_served = Prompt.ask("\u23F0 Enter time served (HH:MM)", default="11:30")
    if time_served.lower() == 'q':
        console.print("\n\U0001F44B Quit requested. Exiting...", style="bold yellow")
        return

    records = []
    clear_screen()

    console.print("\n\u27A1\uFE0F Enter leftovers and ending inventory for each item (type [bold]'q'[/bold] to quit early):\n", style="bold green")

    for _, row in df_sorted.iterrows():
        itemid = row["itemid"]
        itemname = row["itemname"]
        console.print(f"\n[item]{itemname}[/item]")

        leftovers_input = Prompt.ask("  \U0001F37D Leftovers (or 'q' to quit)", default="", show_default=False)
        if leftovers_input.lower() == 'q':
            console.print("\n\U0001F44B Quit requested. Exiting item entry...", style="bold yellow")
            break

        ending_input = Prompt.ask("  \U0001F4E6 Ending Inventory (or 'q' to quit)", default="", show_default=False)
        if ending_input.lower() == 'q':
            console.print("\n\U0001F44B Quit requested. Exiting item entry...", style="bold yellow")
            break

        record = {
            "itemid": itemid,
            "itemname": itemname
        }

        if leftovers_input.strip() != "":
            try:
                record["leftovers"] = float(leftovers_input)
            except ValueError:
                console.print("\u26A0\uFE0F Invalid leftovers input. Skipping item.", style="bold red")
                continue

        if ending_input.strip() != "":
            try:
                record["ending_inv"] = float(ending_input)
            except ValueError:
                console.print("\u26A0\uFE0F Invalid ending inventory input. Skipping item.", style="bold red")
                continue

        if "leftovers" in record or "ending_inv" in record:
            records.append(record)


    if not records:
        console.print("\n\u26A0\uFE0F No data entered. Aborting.", style="bold red")
        return

    # \u2705 Preview table
    table = Table(title="Leftovers & Ending Inventory", show_lines=True)
    table.add_column("Item", style="cyan")
    table.add_column("Leftovers", justify="right")
    table.add_column("Ending Inv", justify="right")

    for rec in records:
        leftovers = rec.get("leftovers", "-")
        ending_inv = rec.get("ending_inv", "-")
        table.add_row(rec["itemname"], str(leftovers), str(ending_inv))


    console.print("\n\U0001F4CB Preview of Data:\n")
    console.print(table)

    # \U0001F4BE Export to Excel
    df_export = pd.DataFrame.from_records(records)
    df_export["serve_date"] = serve_date
    df_export["time_served"] = time_served

    Path(EXPORT_FOLDER).mkdir(exist_ok=True)
    filename = f"{EXPORT_FOLDER}/leftovers_endinginv_{serve_date.replace('-', '')}.xlsx"
    df_export.to_excel(filename, index=False)
    console.print(f"\n\U0001F9FE Data exported to [bold]{filename}[/bold]")

    # \u2705 Confirm before DB insert
    with sqlite3.connect(DB_FILE) as conn:
        for rec in records:
            update_fields = {"time_served": time_served}
            if "leftovers" in rec:
                update_fields["leftovers"] = rec["leftovers"]
            if "ending_inv" in rec:
                update_fields["ending_inv"] = rec["ending_inv"]

            upsert_salad_bar(
                conn,
                rec["itemid"],
                serve_date,
                update_fields
            )

        console.print(f"\n\u2705 {len(records)} records saved to salad_bar table.")

# Run the function
if __name__ == "__main__":
    enter_leftovers_and_ending_inv()
