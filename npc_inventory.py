import sqlite3


class NCPInventory:
    def __init__(self, db_path="npc_inventory.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS inventory
                    (
                    item TEXT PRIMARY KEY,
                    quantitiy INTEGER
                    )
            """)

    def add_item(self, item, quantity=1):
        with self.conn:
            self.conn.execute("""
                INSERT INTO inventory(item, quantity)
                VALUES(?, ?)
                ON CONFLICT(item) DO UPDATE SET quantity = quantity + ?
            """, (item, quantity, quantity))

    def remove_item(self, item, quantity=1):
        with self.conn:
            self.conn.execute("""
                UPDATE inventory SET quantity = quantity - ?
                WHERE item = ? AND quantity >= ?
            """, (quantity, item, quantity))

    def has_item(self, item):
        cur = self.conn.cursor()
        cur.execute("SELECT quantity FROM inventory WHERE item = ?", (item))
        result = cur.fetchone()
        return result is not None and result[0] > 0

    def get_all_items(self):
        cur = self.conn.cursor()
        cur.execute("SELECT item, quantity FROM inventory")
        return cur.fetchall()