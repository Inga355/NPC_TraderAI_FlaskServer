#--------------------------------------------------------------------------------------
# app.py – Main Flask application handling routes and AI chat logic
#--------------------------------------------------------------------------------------

from dotenv import load_dotenv
from flask import Flask, request, send_from_directory, jsonify, send_file, url_for
from flask_cors import CORS
import os
from openai import OpenAI
from pathlib import Path
from agent_tools import tools, parse_trade_intent, trade_consent
from inventory_store import execute_trade, get_inventory
from prompt_generator import build_instructions, build_prompt, build_followup_prompt, build_consent_or_reintent_prompt
from memory_store import add_memory, store_trade_results, load_last_trade_results, get_status_flag, set_status_flag_true, set_status_flag_false
import json
import subprocess


#--------------------------------------------------------------------------------------
# Flask App Setup, OpenAI Client and Serve Chat Interface HTML
#--------------------------------------------------------------------------------------

app = Flask(__name__, static_folder='testfrontend')
CORS(app)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/npc/chat")
def home():
    set_status_flag_false()
    return send_from_directory('testfrontend', 'chatwindow.html')


#--------------------------------------------------------------------------------------
# Main Chat Endpoint – Handles NPC Conversation and Tool Responses
#--------------------------------------------------------------------------------------

@app.route("/npc/chat", methods=["POST"])
def chat():
    player_message_form = request.form.get("userprompt", "")
    # Uncomment if you want to use HTTP request in UE5 (still in testing phase)
    
    #data = request.get_json()
    #player_message_form = data.get("message", "")
    
    npc_response = npc_chat(player_message_form)
    with open("npc_response.txt", "w") as f:
        f.write(npc_response)
    audio_path = Path("speech.mp3")
    return jsonify({
        "text": npc_response,
        "audio_url": url_for('get_audio', filename=audio_path.name, _external=True)
    })


@app.route('/api/audio/<filename>')
def get_audio(filename):
    audio_path = Path(filename)
    return send_file(audio_path, mimetype='audio/mpeg')


#--------------------------------------------------------------------------------------
# Main Function – Handles NPC Conversation and Tool Responses
#--------------------------------------------------------------------------------------

def npc_chat(player_message):
    print(f"PlayerMessage: {player_message}") # Debugging

    if not player_message:
        return "Please provide a message", 400
    
    add_memory(text=player_message, role="user")
    is_trade_ongoing = get_status_flag()
    role_instruction = build_instructions()

    # Process the response and any tool calls
    tool_calls = ""
    results = []
    last_tool_used = []
    trade_state = None
    buy_items = []
    sell_items = []
    consent_result = []

    # Generate AI response depending on weather a trade is ongoing or not
    if not is_trade_ongoing:
        standard_prompt = build_prompt(player_message)
        response = client.responses.create(
            model="gpt-4o",
            instructions=role_instruction,
            input=standard_prompt,
            tools=tools,
            tool_choice="auto"
        )
        add_memory(text=response.output_text, role="assistant")
        tool_calls = response.output
        print(f"Standard-Response-Output: {response.output}")  # Debugging
        print(f"Standard-Response-Output-Text: {response.output_text}")  # Debugging

    elif is_trade_ongoing:
        consent_prompt = build_consent_or_reintent_prompt(player_message)
        response = client.responses.create(
            model="gpt-4o",
            instructions=role_instruction,
            input=consent_prompt,
            tools=tools,
            tool_choice="auto"
        )
        add_memory(text=response.output_text, role="assistant")
        tool_calls = response.output
        print(f"Standard-Response-Output: {response.output}")  # Debugging
        print(f"Standard-Response-Output-Text: {response.output_text}")  # Debugging


    # Check if any tool was called
    if tool_calls and isinstance(tool_calls, list):
        for tool_call in tool_calls:
            if hasattr(tool_call, "arguments"):
                try:
                    args = json.loads(tool_call.arguments)

                    # Process tool call for trade intent
                    if tool_call.name == "parse_trade_intent":
                        set_status_flag_true()
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

                        # Debugging
                        print(f"\033[94mResults: {results}\033[0m")
                        print(f"\033[94mBuy Items: {buy_items}\033[0m")
                        print(f"\033[94mSell Items: {sell_items}\033[0m")
                    
                    # Process tool call for trade consent
                    elif tool_call.name == "trade_consent":
                        consent = args["consent"]
                        consent_result = trade_consent(consent)
                        last_tool_used = "trade_consent"
                        print(f"Consent Result: {consent_result}") # Debugging
                    
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

        print("\033[93mFollow-up GPT Output:\033[0m", followup_response.output) # Debugging
        npc_text = followup_response.output_text or ""
        npc_voice_chat(npc_text)
        return npc_text
        # Uncomment if you want to use HTTP request in UE5 (still in testing phase)
        """
        return jsonify({"response": response_text})
        """

    # Followup after tool trade_consent
    if last_tool_used == "trade_consent" and consent_result:
        player_consent = consent_result["Consent"]
        print(f"\033[93mDebugg PlayerConsent: {player_consent}\033[0m") # Debugging

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
            npc_text_yes = "\n".join(confirmations) + "\nPleasure doing business, matey!"
            print(f"TTS INPUT: {npc_text_yes}")
            npc_voice_chat(npc_text_yes)
            set_status_flag_false()
            return npc_text_yes
            # Uncomment if you want to use HTTP request in UE5 (still in testing phase)
            """
            return jsonify({"response": "\n".join(confirmations) + "\nPleasure doing business, matey!"})
            """

        elif player_consent == "no":
            npc_text_no = "Understood. The trade has been cancelled."
            npc_voice_chat(npc_text_no)
            set_status_flag_false()
            return npc_text_no
            # Uncomment if you want to use HTTP request in UE5 (still in testing phase)
            """
            return jsonify({"response": "Understood. The trade has been cancelled."})
            """

        elif player_consent == "unsure":
            npc_text_unsure = "I'm not sure if you're ready to trade. Let me know when you are!"
            npc_voice_chat(npc_text_unsure)
            set_status_flag_false()
            return npc_text_unsure
            # Uncomment if you want to use HTTP request in UE5 (still in testing phase)
            """
            return jsonify({"response": "I'm not sure if you're ready to trade. Let me know when you are!"})
            """
    
    # Output without tool call
    else:
        add_memory(text=response.output_text, role="assistant")
        print(response.output_text)
        response = response.output_text
        npc_voice_chat(response)
        return response
        # Uncomment if you want to use HTTP request in UE5 (still in testing phase)
        """
        return jsonify({"response": response.output_text})
        """
   


#--------------------------------------------------------------------------------------
# Generate speech from the NPC response and return as audio file
#--------------------------------------------------------------------------------------

def npc_voice_chat(npc_response):
    raw_mp3 = Path(__file__).parent / "speech.mp3"
    final_mp3 = Path("C:/UnrealSounds/speech.mp3")
    text_to_speech = npc_response

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=text_to_speech,
        response_format="mp3",
        instructions="Speak like a snarky pirate.",
    ) as response:
        response.stream_to_file(raw_mp3)
    print(f"NPC voice saved to {raw_mp3}")

    convert_mp3_to_clean_mp3(raw_mp3, final_mp3)
    print(f"Cleaned NPC voice saved to {final_mp3}")

    """
    return send_file(
        speech_file_path,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="npc_voice.mp3"
    )"""

def convert_mp3_to_clean_mp3(raw_path: Path, clean_path: Path):
    subprocess.run([
        "ffmpeg", "-y",                 # -y überschreibt automatisch
        "-i", str(raw_path),
        "-acodec", "libmp3lame",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        str(clean_path)
    ])

#--------------------------------------------------------------------------------------
# Serve SoundFile via API
#-------------------------------------------------------------------------------------- 

@app.route("/api/audio")
def sound():
    speech_file_path = Path("C:/UnrealSounds/speech.mp3")
    return send_file(
        speech_file_path,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name="npc_voice.mp3"
    )

#--------------------------------------------------------------------------------------
# Serve Inventory via API
#-------------------------------------------------------------------------------------- 

@app.route('/api/inventory/<entity_id>', methods=['GET'])
def api_get_inventory(entity_id):
    return get_inventory(entity_id)


#--------------------------------------------------------------------------------------
# Run Flask App
#--------------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000, debug=True)