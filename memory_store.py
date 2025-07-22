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

# Uncomment if ChromaDB is enabled (semantic chat history, still in testing phase)
"""
client = chromadb.PersistentClient(path="vectordb")
collection = client.get_or_create_collection(name="test3")
"""


#--------------------------------------------------------------------------------------
# Store player and assistant messages to chat history
#--------------------------------------------------------------------------------------

def add_memory(text, role):
    """
    Stores a message and its role ('user' or 'assistant') in the chat history table.
    """
    # Uncomment if ChromaDB is enabled (semantic chat history, still in testing phase)
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
    except sqlite3.IntegrityError:
        print("Error: Sqlite IntegrityError occured.")
        
    print("added to memory")


#--------------------------------------------------------------------------------------
# Retrieve recent chat messages from DB
#--------------------------------------------------------------------------------------

def get_recent_chat_messages(limit=20):
    """
    Retrieves the last N messages from chat history.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, text
        FROM chat_history
        ORDER BY timestamp ASC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No chat messages found."

    return [{"role": row[0], "content": row[1]} for row in rows]


#--------------------------------------------------------------------------------------
# Summarize chat history in chunks using OpenAI adn format into JSON with summaries
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
    summarized_messages = summarize_chat_history(chat_messages, summary_interval)

    chat_data = [
        {"role": "system", "content": "You are a helpful assistant. Here's a summary of the recent conversation."},
        *summarized_messages
    ]

    return json.dumps(chat_data, indent=2)


#--------------------------------------------------------------------------------------
# Store and retrieve last trade results for confirmation after tool call parse_trade_intent
#--------------------------------------------------------------------------------------

def store_trade_results(results, entity_id=1, db_path="inventory/inventory.sqlite3"):
    """
    Saves parsed trade result data as system messages in chat_history.
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
    Loads last valid trade result stored as system messages.
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
# Retrieve semantic memories from ChromaDB (if enabled)
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