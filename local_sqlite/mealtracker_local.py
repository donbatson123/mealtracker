def mealtracker():
    import os
    import shutil
    import sqlite3
    from datetime import datetime, date
    from rich.console import Console
    from rich.panel import Panel

    console = Console()
    DB_FILE = "mealtracker.db"
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    history = []

    current_date = date.today()

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_current_meal():
        now = datetime.now().time()
        return 'Breakfast' if now < datetime.strptime("10:30", "%H:%M").time() else 'Lunch'

    def log_error(perm_id, meal, error_message):
        current_time = datetime.now().strftime("%H:%M:%S")
        cursor.execute("""
            INSERT INTO ErrorLogs (perm_id, log_date, log_time, meal_type, error_message)
            VALUES (?, ?, ?, ?, ?);
        """, (perm_id, current_date, current_time, meal, error_message))
        conn.commit()

    def load_used_perm_ids(meal):
        cursor.execute("""
            SELECT perm_id FROM Meals WHERE meals_date = ? AND meal_type = ?;
        """, (current_date, meal))
        return {row[0] for row in cursor.fetchall()}

    def check_perm_id(perm_id, meal):
        cursor.execute("SELECT first_name, last_name, staff FROM students WHERE perm_id = ?", (perm_id,))
        student = cursor.fetchone()
        if student:
            return student
        else:
            console.print("[bold red]No matching student found.[/bold red]")
            log_error(perm_id, meal, "No Student Found")
            return False

    def show_history():
        if history:
            history_text = "\n".join(history[-5:])
            console.print(Panel(history_text, title="[bold yellow]Last 5 Entries[/bold yellow]", style="bold magenta"))

    def center_and_display_name(perm_id):
        columns, _ = shutil.get_terminal_size()
        clear_screen()
        cursor.execute("SELECT first_name, last_name FROM students WHERE perm_id = ?", (perm_id,))
        student = cursor.fetchone()
        if student:
            full_name = f"{student[0]} {student[1]}".center(columns)
            history.append(f"{student[0]} {student[1]}")
        else:
            full_name = f"Student {perm_id}".center(columns)

        console.print(Panel(full_name, style="bold green"))
        console.print("\n[bold cyan]Enter the next PIN code at the bottom:[/bold cyan]")
        show_history()

    def record_meal(perm_id):
        meal = get_current_meal()
        cursor.execute("""
            SELECT COUNT(*) FROM Meals WHERE perm_id = ? AND meals_date = ? AND meal_type = ?;
        """, (perm_id, current_date, meal))
        if cursor.fetchone()[0] > 0:
            console.print("[bold red]This meal record already exists![/bold red]")
            log_error(perm_id, meal, "Record Already Exists")
            return
        try:
            cursor.execute("""
                INSERT INTO Meals (perm_id, meals_date, meal_type)
                VALUES (?, ?, ?);
            """, (perm_id, current_date, meal))
            conn.commit()
            center_and_display_name(perm_id)
        except sqlite3.Error as e:
            console.print(f"[bold red]Error recording meal: {e}[/bold red]")
            conn.rollback()

    # --- App Entry Point ---
    clear_screen()
    console.print(f"\n[bold cyan]Here I am to Save the Day ...  Super MealTracker![/bold cyan]")
    console.print(f"[bold]The date is: {current_date.strftime('%m-%d')}[/bold]")

    while True:
        perm_id = input("Enter PIN Code (or 'q' to quit): ").strip()
        if perm_id.lower() == "q":
            console.print("[bold cyan]Exiting Meal Tracker. Goodbye![/bold cyan]")
            break

        if not perm_id.isdigit():
            console.print("[bold red]Invalid PIN. Please enter a valid numeric PIN.[/bold red]")
            continue

        perm_id = int(perm_id)
        meal = get_current_meal()
        if check_perm_id(perm_id, meal):
            record_meal(perm_id)

    cursor.close()
    conn.close()


# Run the function
if __name__ == "__main__":
    mealtracker()
