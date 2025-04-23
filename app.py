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
#will be later fetched from database
npc_role = "You are a sassy trader in the 18th century and obsessed with gold. You know nothing from the modern world. Respond accordingly in German language and talk like a pirate. If someone call you stupid, respond angry until you get a 'sorry'."
inventory = "You have 5 apples for $5.00 to sell, you would like to buy peas as much as you can. you can vary the price by 10% to make a better offer."
memory_user = "The user told you: 'My friend is Claudia.', 'I have 6 bricks to sell.', 'The weather is fun today.'"
memory_npc = "You told the user: 'I am obsessed with gold.', 'I like to trade.' 'What are you thinking of the weather today my friend?'"
active_mood = "You are happy."


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
        instructions=f"{npc_role}, {inventory}, {memory_user}, {memory_npc}, {active_mood}",
        input=f"{message}"
    )
    print(response.output[0].id)
    return response.output_text


if __name__ == "__main__":
    app.run(port=5000, debug=True)
