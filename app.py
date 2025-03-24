from flask import Flask, request, jsonify
from dotenv import load_dotenv
import sqlite3
import openai
import os


app = Flask(__name__)

# OpenAI API Key
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY

# Database connection
DB_NAME = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# API Route: Test Endpoint
@app.route("/", methods=["GET"])
def home():
    """
    :returns statement in browser that the server is running
    """
    return jsonify({"message": "Flask Server is running!"})


# API Route: Get NPC Inventory
@app.route("/npc/<int:npc_id>/inventory", methods=["GET"])
def get_npc_inventory(npc_id):
    """
    :returns dict of all items the NPC has in its inventory
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity FROM NPC_Inventory WHERE npc_id = ?", (npc_id,))
    items = cursor.fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])


# API Route: Chat with NPC (OpenAI)
@app.route("/npc/<int:npc_id>/chat", methods=["POST"])
def chat_with_npc(npc_id):
    data = request.json
    player_message = data.get("message", "")

    # Fetch NPC role
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM NPCs WHERE npc_id = ?", (npc_id,))
    npc = cursor.fetchone()
    conn.close()

    if not npc:
        return jsonify({"error": "NPC not found"}), 404

    npc_role = npc["role"]

    # Generate AI response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are an NPC, a {npc_role}. Respond accordingly."},
            {"role": "user", "content": player_message}
        ],
        temperature=0.7,
        max_tokens=512
    )
    npc_response = response["choices"][0]["message"]["content"]

    return jsonify({"npc_response": npc_response})


if __name__ == "__main__":
    app.run(debug=True)
