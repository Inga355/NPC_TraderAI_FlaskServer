from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from openai import OpenAI
from agent_tools import tools, parse_trade_intent, trade_consent
from prompt_generator import build_instructions, build_prompt, build_followup_prompt
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
    last_tool_used = []
    trade_state = None
    buy_items = []
    sell_items = []
    consent_result = []

    # Check if any tool was called
    if tool_calls and isinstance(tool_calls, list):
        for tool_call in tool_calls:
            if hasattr(tool_call, "arguments"):
                try:
                    args = json.loads(tool_call.arguments)
                    
                    # Process tool call for trade intent
                    if tool_call.name == "parse_trade_intent":
                        trade_state = args["trade_state"]
                        item = args["item"]
                        quantity = args["quantity"]
                        result = parse_trade_intent(trade_state, item, quantity)
                        results.append(result)
                        last_tool_used = "parse_trade_intent"

                        if result["trade_state"] == "buy":
                            buy_items.append(result)       
                        elif result["trade_state"] == "sell":
                            sell_items.append(result)
                    
                    # Process tool call for trade consent
                    elif tool_call.name == "trade_consent":
                        consent = args["consent"]
                        consent_result = trade_consent(consent)
                        last_tool_used = "trade_consent"
                        print(f"Consent Result: {consent_result}")
                    
                    else:
                        print(f"Unknown Tool: {tool_call.name}")

                except Exception as e:
                    print(f"Error processing tool arguments: {e}")
            else:
                print("Tool call without arguments field detected!")
   
    # Followup after tool parse_trade_intent
    if last_tool_used == "parse_trade_intent" and results:  
        followup_prompt = build_followup_prompt(buy_items, sell_items)

        # New API call to execute confirmation call
        followup_response = client.responses.create(
            model="gpt-4o",
            instructions=role_instruction,
            input=followup_prompt
        )

        print("Follow-up GPT Output:", followup_response.output)
        response_text = followup_response.output_text or "" 
        return response_text
    
    # Output without tool call
    else:
        return response.output_text
    
"""
    # Init followup response to ask for confirmation
    if response_text == '':
        followup_response = client.responses.create(
            model="gpt-4o",
            instructions=role_instruction,
            input=build_followup_prompt(buy_items, sell_items),
        )
        # Format the output
        followup_response_text = followup_response.output_text"""   


"""    # Format the output from tool call
    for result in results:
        if result["trade_state"] == "buy":
            buy_items.append(result)           
        elif result["trade_state"] == "sell":
            sell_items.append(result)
                   
    print("Buy Items:", buy_items)
    print("Sell Items:", sell_items)
"""    
 

if __name__ == "__main__":
    app.run(port=5000, debug=True)