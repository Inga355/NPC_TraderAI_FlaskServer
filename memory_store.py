import os
import chromadb
import json
import sqlite3
import uuid
from datetime import datetime
from openai import OpenAI

"""
# Creating a persistent Client
client = chromadb.PersistentClient(path="vectordb")

# Creates the collecting if not yet exists or get the collection from the client
collection = client.get_or_create_collection(name="test3")
"""

# OpenAI GPT client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database path
db_path = "inventory/inventory.sqlite3"


#--------------------------------------------------------------------------------------
# Adding the Chathistory to Database
#--------------------------------------------------------------------------------------

def add_memory(text, role):
    """
    Adds the User-Prompt and NPC-Answer to chat_history table and to the memory collection.
    :param text: the answer that is displayed to the user from OpenAi Api or the user prompt
    :param role: 'user' or 'assistant'
    :return: None
    """
    # Add to memory collection
    """
    id = str(uuid.uuid4())
    collection.add(
        documents=[text],
        metadatas=[{"created": str(datetime.now()), "role": f"{role}"}],
        ids=[id]
    )
    """

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


#--------------------------------------------------------------------------------------
# Getting Chathistory from DB
#--------------------------------------------------------------------------------------

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

    return [{"role": row[0], "content": row[1]} for row in rows]
"""
    # build text for prompt
    history_lines = []
    for role, text in rows:
        role_name = "Player" if role == "user" else "You"
        history_lines.append(f"{role_name}: {text}")

    return "\n".join(history_lines)"""


def summarize_chat_history(chat_messages, summary_interval=5):
    """
    Erstelle eine Zusammenfassung nach jeder 'summary_interval' Anzahl von Nachrichten.
    """
    summaries = []
    
    for i in range(0, len(chat_messages), summary_interval):
        chunk = chat_messages[i:i+summary_interval]
        texts = "\n".join([msg["content"] for msg in chunk])

        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": "Fasse die folgende Unterhaltung zusammen. Der Händler ('role': 'assistant') ist ein NPC in einen Role Play Game und der Käufer ('role': 'user') ist der Spieler, der zu dem NPC spricht. Beachte das in der Zusammenfassung."},
                {"role": "user", "content": texts}
            ]
        )
        
        summary = response.output_text
        summaries.append({"summary": summary, "messages": chunk})

    return summaries


def format_chat_history_as_json(limit=20, summary_interval=5):
    """
    Extrahiere Nachrichten, erstelle Zusammenfassungen und gebe sie im JSON-Format aus.
    """
    chat_messages = get_recent_chat_messages(limit)
    summarized_messages = summarize_chat_history(chat_messages, summary_interval)

    chat_data = [
        {"role": "system", "content": "Du bist ein hilfreicher Assistent. Hier ist eine Zusammenfassung der letzten Nachrichten"},
        *summarized_messages
    ]

    return json.dumps(chat_data, indent=2)

#--------------------------------------------------------------------------------------
# Handle the trade intent - storing and recieving the current intent
#--------------------------------------------------------------------------------------

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


#--------------------------------------------------------------------------------------
# Getting memories fron Vector DB
#--------------------------------------------------------------------------------------

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


#--------------------------------------------------------------------------------------
# TESTER
#--------------------------------------------------------------------------------------

#print(format_chat_history_as_json(limit=10, summary_interval=3))