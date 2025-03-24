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



