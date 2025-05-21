import sqlite3

from inventory_store import get_all_items


def setup_database(db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL UNIQUE,
            role TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Add Test NPC
def insert_entity(entity_type, entity_name, role=None, db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO entities (type, name, role)
            VALUES (?, ?, ?)
            """, (entity_type, entity_name, role))
        conn.commit()
        return f"added {entity_type.capitalize()} '{entity_name}' to database"
    except sqlite3.IntegrityError:
        return f"Error: Entity '{entity_name}' already exists."
    finally:
        conn.close()


if __name__ == "__main__":
    # Ensure database and table exist
    #setup_database()
    # Try to insert the test NPC
    #result = insert_entity("npc", "Drunken Johnny Delgado", "A sassy trader in the 18th century and obsessed with gold. You know nothing from the modern world. Respond accordingly. If someone refers to any modern thing you get mad and call him out.")
    print(get_all_items(entity_id=1))
