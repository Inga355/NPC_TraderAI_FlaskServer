import sqlite3
import json
from datetime import datetime


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
    

#--------------------------------------------------------------------------------------
# Handle the trade by updating DB and givng confirmation to player
#--------------------------------------------------------------------------------------

def execute_trade(trade_state, item_name, quantity, player_id=2, npc_id=1, db_path="inventory/inventory.sqlite3"):
    """
    Executes the trade: Player buys from or sells to NPC.
    Adjust quantities in inventory and returns a confirmation message.
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get item id
    cursor.execute("SELECT id FROM items WHERE name = ?", (item_name,))
    item_row = cursor.fetchone()
    if not item_row:
        conn.close()
        return f"Arrr, I ain't got no '{item_name}' in me ledgers!"
    item_id = item_row[0]

    # Get price
    cursor.execute("SELECT price FROM prices WHERE item_id = ?", (item_id,))
    price_row = cursor.fetchone()
    price_per_unit = price_row[0] if price_row else 0
    total_price = price_per_unit * quantity

    # Helper: Inventory check
    def get_quantity(entity_id):
        cursor.execute("""
            SELECT quantity FROM inventory WHERE entity_id = ? AND item_id = ?
        """, (entity_id, item_id))
        row = cursor.fetchone()
        return row[0] if row else 0

    # Helper: Inventory update
    def update_inventory(entity_id, delta_qty):
        current_qty = get_quantity(entity_id)
        new_qty = current_qty + delta_qty
        if current_qty == 0:
            cursor.execute("""
                INSERT INTO inventory (entity_id, item_id, quantity)
                VALUES (?, ?, ?)
            """, (entity_id, item_id, max(new_qty, 0)))
        else:
            cursor.execute("""
                UPDATE inventory SET quantity = ?
                WHERE entity_id = ? AND item_id = ?
            """, (max(new_qty, 0), entity_id, item_id))

    # Trading logic
    if trade_state == "buy":
        npc_stock = get_quantity(npc_id)
        if npc_stock < quantity:
            conn.close()
            return f"Arrr, I only got {npc_stock} {item_name}(s) in me stash!"

        update_inventory(npc_id, -quantity)
        update_inventory(player_id, quantity)
        conn.commit()
        conn.close()
        return f"Ye bought {quantity} {item_name}(s) for {total_price:.2f} gold."

    elif trade_state == "sell":
        player_stock = get_quantity(player_id)
        if player_stock < quantity:
            conn.close()
            return f"Ye trying to cheat me? Ye only got {player_stock} {item_name}(s)!"

        update_inventory(player_id, -quantity)
        update_inventory(npc_id, quantity)
        conn.commit()
        conn.close()
        return f"Sold {quantity} {item_name}(s) for {total_price:.2f} gold. Ye drive a hard bargain!"

    else:
        conn.close()
        return "I don't understand if ye be buyin' or sellin', matey!"

