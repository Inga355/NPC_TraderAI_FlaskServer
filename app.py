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
    return jsonify({"message": "Flask Server is running!"})


# API Route: Get NPC Inventory
@app.route("/npc/<int:npc_id>/inventory", methods=["GET"])
def get_npc_inventory(npc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity FROM NPC_Inventory WHERE npc_id = ?", (npc_id,))
    items = cursor.fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])



