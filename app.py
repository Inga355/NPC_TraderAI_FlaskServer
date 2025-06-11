from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from agent_tools import tools, parse_trade_intent, trade_consent
from inventory_store import execute_trade
from prompt_generator import build_instructions, build_prompt, build_followup_prompt
from memory_store import add_memory, store_trade_results, load_last_trade_results
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
    #player_message = request.form.get("userpromt", "")
    data = request.get_json()
    player_message = data.get("Message", "")
    print(f"PlayerMessage: {player_message}")

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
    print(response.usage.input_tokens)
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
                        store_trade_results(results)
                        last_tool_used = "parse_trade_intent"

                        if result["trade_state"] == "buy":
                            buy_items.append(result)       
                        elif result["trade_state"] == "sell":
                            sell_items.append(result)

                        # Just for Debugging
                        print(f"\033[94mResults: {results}\033[0m")
                        print(f"\033[94mBuy Items: {buy_items}\033[0m")
                        print(f"\033[94mSell Items: {sell_items}\033[0m")    
                    
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

        print("\033[93mFollow-up GPT Output:\033[0m", followup_response.output)
        response_text = followup_response.output_text or "" 
        #return response_text
        return jsonify({"response": response_text})
    
    # Followup after tool trade_consent
    if last_tool_used == "trade_consent" and consent_result:
        player_consent = consent_result["Consent"]
        print(f"\033[93mDebugg PlayerConsent: {player_consent}\033[0m")

        """
        Can later be improved by handling per GPT and adding sentiments
        """
        if player_consent == "yes":
            confirmations = []
            results = load_last_trade_results(1)
            print(f"\033[92mResultsHandling: {results}\033[0m")
            for result in results:
                trade_state = result["trade_state"]
                item_name = result["item"]
                quantity = result["quantity"]
                message = execute_trade(trade_state, item_name, quantity)
                confirmations.append(message)         
            #return "\n".join(confirmations) + "\nPleasure doing business, matey!"
            return jsonify({"response": "\n".join(confirmations) + "\nPleasure doing business, matey!"})

        elif player_consent == "no":
            #return "Understood. The trade has been cancelled."
            return jsonify({"response": "Understood. The trade has been cancelled."})

        elif player_consent == "unsure":
            #return "I'm not sure if you're ready to trade. Let me know when you are!"
            return jsonify({"response": "I'm not sure if you're ready to trade. Let me know when you are!"})
    
    # Output without tool call
    else:
        #return response.output_text
        return jsonify({"response": response.output_text})
    
 

if __name__ == "__main__":
    app.run(port=5000, debug=True)