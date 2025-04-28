from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI
from inventory_store import get_all_items, get_entity_role
from memory_store import add_memory, get_memories_from_npc, get_memories_from_player



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
npc_name = "Drunken Johnny Delgado"
npc_role = "A sassy trader in the 18th century and obsessed with gold. You know nothing from the modern world. Respond accordingly. If someone refers to any modern thing you get mad and call him out."
#inventory = "You have 5 apples for $5.00 to sell, you would like to buy peas as much as you can. you can vary the price by 10% to make a better offer."


def build_prompt(player_input):
    memories_player = get_memories_from_player(player_input)
    memories_npc = get_memories_from_npc(player_input)

    formatted_memories_player = "\n".join(f"- {m}" for m in memories_player)
    print(formatted_memories_player)
    formatted_memories_npc = "\n".join(f"- {m}" for m in memories_npc)
    print(formatted_memories_npc)

    inventory_npc = get_all_items(1)

    prompt = f"""
These are your memories of what the player has told you:
{formatted_memories_player}

These are your memories of what you have told the player:
{formatted_memories_npc}

These are the items you have to sell:
{inventory_npc}
Make your offer wisely, do not offer all items at once, make it dependent on the conversation content, what you offer!

Now the player is speaking to you. Respond appropriately according to your role, character, and memories. Use the memories only if you decide it gives context, better understanding of a situation or benefit for the conversation.

Player says: "{player_input}"
"""
    return prompt.strip()


# API Route: Chat with NPC (OpenAI)
@app.route("/npc/chat", methods=["POST"])
def npc_chat():
    player_message = request.form.get("userpromt", "")

    if not player_message:
        return "Please provide a message", 400
    
    add_memory(text=player_message, role="user")

    message = build_prompt(player_message)

    # Generate AI response
    response = client.responses.create(
        model="gpt-4o",
        instructions=f"Your name is {npc_name} and you are {npc_role}. You have a good memory and remember past conversations or important information. Use the memories only if you decide that it is necessary to provide accurate context.",
        input=message
    )

    add_memory(text=(response.output_text), role="assistant")
    
    return response.output_text


if __name__ == "__main__":
    app.run(port=5000, debug=True)
