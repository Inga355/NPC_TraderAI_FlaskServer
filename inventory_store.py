import sqlite3


def get_all_items(entity_id, db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL: Entity, Item-Namen, Menge, Preis abrufen
    cursor.execute("""
        SELECT
            i.name AS item_name,
            inv.quantity,
            IFNULL(p.price, 0) AS price
        FROM inventory inv
        JOIN entities e ON inv.entity_id = e.id
        JOIN items i ON inv.item_id = i.id
        LEFT JOIN prices p ON p.item_id = i.id
        WHERE e.id = ?
    """, (entity_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"{entity_id} has no inventory or no items."

    # Formatted Output
    output = [f"{entity_id} has these items in inventory:"]
    for item_name, quantity, price in rows:
        output.append(f"- {quantity} {item_name} at ${price:.2f} each")

    return "\n".join(output)


def insert_item(name, description="", db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO items (name, description)
            VALUES (?, ?)
        """, (name, description))
        conn.commit()
        return f"Item '{name}' wurde erfolgreich hinzugefügt."
    except sqlite3.IntegrityError:
        return f"Fehler: Item mit dem Namen '{name}' existiert bereits."
    finally:
        conn.close()


def get_entity_name(id, db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name FROM entities WHERE id = ?
    """, (id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return f"{result[0]}"
    elif result:
        return f"'{id}' has no specific name."
    else:
        return f"No entity with '{id}' found."


def get_entity_role(id, db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role FROM entities WHERE id = ?
    """, (id,))
    result = cursor.fetchone()
    conn.close()

    if result and result[0]:
        return f"{result[0]}"
    elif result:
        return f"'{id}' has no specific role."
    else:
        return f"No entity with '{id}' found."
    


print(get_all_items(1))
print(get_entity_name(1))
print(get_entity_role(1))