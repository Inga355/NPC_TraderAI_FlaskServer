import os
import chromadb
import json
import sqlite3
import uuid
from datetime import datetime
from openai import OpenAI


# Creating a persistent Client
client = chromadb.PersistentClient(path="vectordb")

# Creates the collecting if not yet exists or get the collection from the client
collection = client.get_or_create_collection(name="test3")

# Database path
db_path = "inventory/inventory.sqlite3"


def add_memory(text, role):
    """
    Adds the User-Prompt and NPC-Answer to chat_history table and to the memory collection.
    :param text: the answer that is displayed to the user from OpenAi Api or the user prompt
    :param role: 'user' or 'assistant'
    :return: None
    """
    # Add to memory collection
    id = str(uuid.uuid4())
    collection.add(
        documents=[text],
        metadatas=[{"created": str(datetime.now()), "role": f"{role}"}],
        ids=[id]
    )

    # Add to chat_history table
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


def get_memories_from_player(text):
    """
    Get the best fitting 3 user prompts from the memory collection.
    :param text: the user prompt
    :return: the best fitting 3 user prompts
    """
    results = collection.query(
        query_texts=[text],
        n_results=3,
        where={"role": "user"}
    )
    return results["documents"][0]


def get_memories_from_npc(text):
    """
    Get the best fitting 3 NPC answers from the memory collection.
    :param text: the user prompt
    :return: the best fitting 3 NPC answers
    """
    results = collection.query(
        query_texts=[text],
        n_results=3,
        where={"role": "assistant"}
    )
    return results["documents"][0]


def get_recent_chat_messages(limit=20):
    """
    Get the last n- messages from the chat_history table.
    :param limit: the number of messages to get
    :return: the last n- messages
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # returns last n- messages
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

    # build text for prompt
    history_lines = []
    for role, text in rows:
        role_name = "Player" if role == "user" else "You"
        history_lines.append(f"{role_name}: {text}")

    return "\n".join(history_lines)

# Store function for trade intents in chat_history (after parse_trade_intent tool call)
def store_trade_results(results, entity_id=1, db_path="inventory/inventory.sqlite3"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history (timestamp, entity_id, role, text)
        VALUES (?, ?, ?, ?)
    """, (datetime.now(), entity_id, "system", json.dumps(results)))

    conn.commit()
    conn.close()
    return "Results saved."


# Loading function for the last stored trading intent
def load_last_trade_results(entity_id=1, db_path="inventory/inventory.sqlite3"):
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


# Initalize OpenAi
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Embedding model
#embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
#index = pc.Index(INDEX_NAME)
#print(embeddings)
