# main_menu.py
import sys
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from enter_leftovers_inv import enter_leftovers_and_ending_inv
from enter_orders import enter_orders
from enter_units_rcvd import enter_units_rcvd_data
from mealtracker_local import mealtracker
from sync_meals_orders import sync_meals_orders
from sync_students_from_postgres import sync_students_from_postgres
from student_entry import add_students

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_menu():
    clear_screen()
    console.print(Panel.fit("🥗 [bold cyan]MEALTRACKER MAIN MENU[/bold cyan]", border_style="green"))
    console.print("""
[1] ➕ Enter Orders
[2] 🍽 Enter Leftovers & Ending Inventory
[3] 📦 Enter Produce Received
[4] 📊 Run MealTracker
[5] 🔄 Add New Students to local SQLite db
[6] 🔄 Sync Meals/Orders/Salad Bar to PostgreSQL
[7] 👥 Update Students from PostgreSQL
[q] ❌ Quit
""", style="bold")


def main():
    while True:
        try:
            show_menu()
            choice = Prompt.ask("Pick an option", choices=["1", "2", "3", "4", "5", "6", "7", "q"], default="q")
            
            if choice == "1":
                console.print("▶️ [yellow]Orders function not wired up yet[/yellow]")
                enter_orders()
            elif choice == "2":
                enter_leftovers_and_ending_inv()
            elif choice == "3":
                console.print("📦 [yellow]Ending Inventory logic goes here[/yellow]")
                enter_units_rcvd_data()
            elif choice == "4":
                console.print("📊 [yellow]MealTracker function not wired up yet[/yellow]")
                mealtracker()
            elif choice == "5":
                console.print("📊 [yellow]add students to local SQLite db function not wired up yet[/yellow]")
                add_students()
            elif choice == "6":
                console.print("📊 [yellow]sync meals/orders/sala_bar to postgres function not wired up yet[/yellow]")
                sync_meals_orders(dry_run=False)
            elif choice == "7":
                console.print("📊 [yellow]update students function not wired up yet[/yellow]")
                sync_students_from_postgres()
            elif choice == "q":
                console.print("\n👋 See you next meal!", style="bold green")
                break

            input("\n🔁 Press [Enter] to return to the menu...")

        except KeyboardInterrupt:
            console.print("\n\n🚪 Graceful exit. Bye!", style="bold red")
            sys.exit()

if __name__ == "__main__":
    main()
