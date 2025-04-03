import sqlite3

DB_NAME = "database.db"


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Players Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # NPCs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NPCs (
            npc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            description TEXT,
            base_value INTEGER NOT NULL DEFAULT 0,
            rarity TEXT CHECK(rarity IN ('common', 'uncommon', 'rare', 'epic', 'legendary')) NOT NULL
        )
    ''')

    # NPC Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NPC_Inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            npc_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (npc_id) REFERENCES NPCs(npc_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE
        )
    ''')

    # Player Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Player_Inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE
        )
    ''')

    # Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ChatHistory (
            chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            npc_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            sender TEXT CHECK(sender IN ('player', 'npc')) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
            FOREIGN KEY (npc_id) REFERENCES NPCs(npc_id) ON DELETE CASCADE
        )
    ''')

    # Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            npc_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('buy', 'sell', 'trade')) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
            FOREIGN KEY (npc_id) REFERENCES NPCs(npc_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES Items(item_id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database and tables initialized successfully!")


if __name__ == "__main__":
    create_tables()
