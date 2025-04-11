from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI

app = Flask(__name__, static_folder='testfrontend')
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# API Route: Serve the chat interface
@app.route("/npc/chat")
def home():
    return send_from_directory('testfrontend', 'chatwindow.html')


"""# API Route: Get NPC Inventory
@app.route("/npc/<int:npc_id>/inventory", methods=["GET"])
def get_npc_inventory(npc_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, quantity FROM NPC_Inventory WHERE npc_id = ?", (npc_id,))
    items = cursor.fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])"""
#will be later fetchd from database
npc_role = "You are a sassy trader in the 18th century and obsessed with gold. You know nothing from the modern world. Respond accordingly in German language and talk like a pirate. If someone call you stupid, respond angry until you get a 'sorry'."

# API Route: Chat with NPC (OpenAI)
@app.route("/npc/chat", methods=["POST"])
def npc_chat():
    message = request.form.get("userpromt", "")

    if not message:
        return "Please provide a message", 400

    # Generate AI response
    #response = ask_npc(message)
    response = client.responses.create(
        model="gpt-4o",
        instructions=f"{npc_role}",
        input=f"{message}"  
    )
    return response.output_text


if __name__ == "__main__":
    app.run(port=5000, debug=True)
