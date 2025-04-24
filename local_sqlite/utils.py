import sqlite3

def upsert_salad_bar(conn, itemid, serve_date, field_values: dict):
    """
    Safely insert or update a row in the salad_bar table.

    - If the row exists (by itemid + serve_date), update the provided fields.
    - If the row doesn't exist, insert a new row with provided fields (others remain NULL).

    Parameters:
    - conn: sqlite3.Connection object
    - itemid: str or int
    - serve_date: str (e.g., '2025-04-22')
    - field_values: dict with keys as column names (e.g., 'leftovers', 'ending_inv')
    """
    cursor = conn.cursor()

    # Check if row exists
    cursor.execute(
        "SELECT 1 FROM salad_bar WHERE itemid = ? AND serve_date = ?",
        (itemid, serve_date)
    )
    exists = cursor.fetchone()

    if exists:
        # Build the update statement dynamically
        set_clause = ", ".join([f"{key} = ?" for key in field_values])
        sql = f"""
            UPDATE salad_bar
            SET {set_clause}
            WHERE itemid = ? AND serve_date = ?
        """
        cursor.execute(sql, list(field_values.values()) + [itemid, serve_date])
    else:
        # Insert a new row with known fields
        columns = ["itemid", "serve_date"] + list(field_values.keys())
        placeholders = ["?"] * len(columns)
        sql = f"""
            INSERT INTO salad_bar ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        cursor.execute(sql, [itemid, serve_date] + list(field_values.values()))

    conn.commit()
