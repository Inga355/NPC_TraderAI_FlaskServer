from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI
from agent_tools import tools, parse_item_and_quantity
from prompt_generator import build_instructions, build_prompt
from memory_store import add_memory
import json



app = Flask(__name__, static_folder='testfrontend')
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# API Route: Serve the chat interface
@app.route("/npc/chat")
def home():
    return send_from_directory('testfrontend', 'chatwindow.html')


# API Route: Chat with NPC (OpenAI)
@app.route("/npc/chat", methods=["POST"])
def npc_chat():
    player_message = request.form.get("userpromt", "")

    if not player_message:
        return "Please provide a message", 400
    
    add_memory(text=player_message, role="user")

    role_instruction = build_instructions()
    message = build_prompt(player_message)

    # Generate AI response
    response = client.responses.create(
        model="gpt-4o",
        instructions=role_instruction,
        input=message,
        tools=tools,
        tool_choice="auto" # LLM decides by itself to use tools or not
    )

    add_memory(text=(response.output_text), role="assistant")
    
    # Process the response and any tool calls
    print(response.output)
    tool_calls = response.output
    results = []

    if tool_calls and isinstance(tool_calls, list):
        for tool_call in tool_calls:
            if hasattr(tool_call, "arguments"):
                try:
                    args = json.loads(tool_call.arguments)
                    result = parse_item_and_quantity(**args)
                    results.append(result)
                except Exception as e:
                    print(f"Fehler beim Verarbeiten der Tool-Argumente: {e}")
            else:
                print("Tool-Call ohne arguments-Feld erkannt.")

    for result in results:
        print("ToolOutput:",result)

    response_text = response.output_text

    if response_text == '':
        followup_response = client.responses.create(
            model="gpt-4o",
            instructions=role_instruction,
            input=message
        )

        print(f"I have used a tool.")

        followup_response_text = followup_response.output_text
        return followup_response_text
    else:
        return response_text


if __name__ == "__main__":
    app.run(port=5000, debug=True)