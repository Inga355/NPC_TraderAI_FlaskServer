#--------------------------------------------------------------------------------------
# memory_store.py – Handles chat memory, summaries, and trade logging via SQLite and ChromaDB
#--------------------------------------------------------------------------------------

import os
import chromadb
import json
import sqlite3
import uuid
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv


#--------------------------------------------------------------------------------------
# Configuration and Clients
#--------------------------------------------------------------------------------------

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
db_path = "inventory/inventory.sqlite3"

# Uncomment this block if ChromaDB is enabled (semantic chat history, still in testing phase)
"""
client = chromadb.PersistentClient(path="vectordb")
collection = client.get_or_create_collection(name="test3")
"""


#--------------------------------------------------------------------------------------
# Store messages to chat history
#--------------------------------------------------------------------------------------

def add_memory(text, role, db_path="inventory/inventory.sqlite3"):
    """
    Stores a message from the chat in the SQLite database, along with its role and timestamp.
    :param text: (str) Message content to store.
    :param role: (str) Sender role, typically 'user','assistant' or 'system'.
    :param db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: None
    Notes:
        - Optional semantic storage via ChromaDB can be enabled (commented out).
        - Timestamp is automatically assigned during insertion.
    """
    # Uncomment this block if ChromaDB is enabled (semantic chat history, still in testing phase)
    """
    id = str(uuid.uuid4())
    collection.add(
        documents=[text],
        metadatas=[{"created": str(datetime.now()), "role": f"{role}"}],
        ids=[id]
    )
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = str(datetime.now())

    try:
        cursor.execute("""
            INSERT INTO chat_history (timestamp, role, text)
            VALUES (?, ?, ?)
        """, (timestamp, role, text))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Error: Sqlite IntegrityError occurred.")
        
    print(f"{role}: added to memory")


#--------------------------------------------------------------------------------------
# Retrieve recent chat messages from DataBase
#--------------------------------------------------------------------------------------

def get_recent_chat_messages(limit=50, db_path="inventory/inventory.sqlite3"):
    """
    Fetches the most recent chat exchanges between user and assistant,
    sorted chronologically for conversational context reconstruction.
    :param limit: (int, optional) Number of chat messages to retrieve. Defaults to 50.
    :param db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: list[dict] | str: List of message dictionaries containing role and content,
            or a message string if no records are found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, text
        FROM (
            SELECT role, text, timestamp
            FROM chat_history
            WHERE role IN ('user', 'assistant') AND TRIM(text) <> ''
            ORDER BY timestamp DESC
            LIMIT ?
        ) AS sub
        ORDER BY timestamp ASC
        """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No chat messages found."

    return [{"role": row[0], "content": row[1]} for row in rows]


#--------------------------------------------------------------------------------------
# Status Flag for ongoing Trade
#--------------------------------------------------------------------------------------

def get_status_flag(db_path="inventory/inventory.sqlite3"):
    """
    Retrieves the current trade status flag from the database.
    :param db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: bool | str: Returns True if a trade is ongoing (is_active == 1),
            False if no active trade, or a message string if no flag record is found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
                SELECT is_active FROM status_flag WHERE id = 1
                """)
    except sqlite3.IntegrityError:
        print("Error: Sqlite IntegrityError occurred.")

    row = cursor.fetchone()
    conn.close()

    if not row:
        return "No status_flag found."

    is_trade_ongoing = bool(row[0])
    return is_trade_ongoing


def set_status_flag_true(db_path="inventory/inventory.sqlite3"):
    """
    Activates the trade status flag in the database.
    :param db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
            UPDATE status_flag SET is_active = 1 WHERE id = 1
            """)
    conn.commit()
    conn.close()
    print("Status_flag set to True")


def set_status_flag_false(db_path="inventory/inventory.sqlite3"):
    """
    Deactivates the trade status flag in the database.
    :param db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
            UPDATE status_flag SET is_active = 0 WHERE id = 1
            """)
    conn.commit()
    conn.close()
    print("Status_flag set to False")


#--------------------------------------------------------------------------------------
# Store and retrieve last trade results for confirmation after tool call parse_trade_intent
#--------------------------------------------------------------------------------------

def store_trade_results(results, entity_id=1, db_path="inventory/inventory.sqlite3"):
    """
    Stores parsed trade results in the chat_history table of the database.
    The results are serialized as JSON and saved as a system message
    associated with the given entity_id. This is used to log the output
    of trade parsing operations and enable later retrieval for confirmation.
    :param results: (list or dict) Parsed trade data, typically a list of trade dicts.
    :param entity_id: (int) Identifier for the trade entity or user (default is 1).
    :param db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: Confirmation message indicating successful storage.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (timestamp, entity_id, role, text)
        VALUES (?, ?, ?, ?)
    """, (datetime.now(), entity_id, "system", json.dumps(results)))

    conn.commit()
    conn.close()
    return "Results saved."


def load_last_trade_results(entity_id=1, db_path="inventory/inventory.sqlite3"):
    """
    Retrieves the most recent valid trade results from chat_history for a given entity.
    :param entity_id: (int) Identifier for the trade entity or user (default is 1).
    :param db_path: db_path: (str, optional) Path to SQLite database file. Defaults to 'inventory/inventory.sqlite3'.
    :return: (list) Parsed trade results if found, otherwise an empty list.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT text FROM chat_history
        WHERE entity_id = ? AND role = 'system'
        ORDER BY id DESC LIMIT 10
    """, (entity_id,))
    rows = cursor.fetchall()
    conn.close()

    for (text,) in rows:
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list) and all("trade_state" in r for r in parsed):
                return parsed
        except json.JSONDecodeError:
            continue

    return []


#--------------------------------------------------------------------------------------
# Summarize chat history in chunks using OpenAI adn format into JSON with summaries

# WORK IN PROGRESS!!
#--------------------------------------------------------------------------------------

def summarize_chat_history(chat_messages, summary_interval=5):
    """
    Summarizes chat messages in chunks of summary_interval.
    """
    summaries = []
    
    for i in range(0, len(chat_messages), summary_interval):
        chunk = chat_messages[i:i+summary_interval]
        texts = "\n".join([msg["content"] for msg in chunk])

        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": "Summarize the following conversation. The merchant ('role': 'assistant') is an NPC in a role-playing game and the buyer ('role': 'user') is the player who is talking to the NPC. Consider this in the summary."},
                {"role": "user", "content": texts}
            ]
        )
        
        summary = response.output_text
        summaries.append({"summary": summary, "messages": chunk})

    return summaries


def format_chat_history_as_json(limit=20, summary_interval=5):
    """
    Returns chat history and summaries as JSON.
    """
    chat_messages = get_recent_chat_messages(limit)
    #summarized_messages = summarize_chat_history(chat_messages, summary_interval)

    chat_data = [
        {"role": "system", "content": "You are a helpful assistant. Here's a summary of the recent conversation."},
        *chat_messages
    ]

    return json.dumps(chat_data, indent=2)


#--------------------------------------------------------------------------------------
# Retrieve semantic memories from ChromaDB (if enabled)

# WORK IN PROGRESS!!
#--------------------------------------------------------------------------------------

def get_memories_from_player(text):
    """
    Retrieves 3 most relevant player messages from vector DB.
    """
    results = collection.query(
        query_texts=[text],
        n_results=3,
        where={"role": "user"}
    )
    return results["documents"][0]


def get_memories_from_npc(text):
    """
    Retrieves 3 most relevant NPC replies from vector DB.
    """
    results = collection.query(
        query_texts=[text],
        n_results=3,
        where={"role": "assistant"}
    )
    return results["documents"][0]


