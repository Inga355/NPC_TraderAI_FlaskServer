import os
import chromadb
import sqlite3
import uuid
from datetime import datetime
from openai import OpenAI


# Creating a persistent Client
client = chromadb.PersistentClient(path="vectordb")

# Creates the collecting if not yet exists or get the collection from the client
collection = client.get_or_create_collection(name="test3")
db_path = "inventory/inventory.sqlite3"

def add_memory(text, role):
    """
    Adds the NPC-Answer to the database.
    :param text: the answer that is displayed to the user from OpenAi Api or the user prompt
    :param role: 'user' or 'assistant'
    :return: None
    """
    id = str(uuid.uuid4())
    collection.add(
        documents=[text],
        metadatas=[{"created": str(datetime.now()), "role": f"{role}"}],
        ids=[id]
    )

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
    results = collection.query(
        query_texts=[text],
        n_results=3,
        where={"role": "user"}
    )
    return results["documents"][0]


def get_memories_from_npc(text):
    results = collection.query(
        query_texts=[text],
        n_results=3,
        where={"role": "assistant"}
    )
    return results["documents"][0]


def get_recent_chat_messages(limit=20, db_path="inventory/inventory.sqlite3"):
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


# Initalize OpenAi
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Embedding model
#embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
#index = pc.Index(INDEX_NAME)
#print(embeddings)
