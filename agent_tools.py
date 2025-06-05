def parse_trade_intent(trade_state: str="no trade", item: str="null", quantity: int=0):
    # Handle plural forms
    item = item.lower()  # Convert to lowercase for consistency
    if item.endswith('s'):
        item = item[:-1]  # Remove trailing 's' for singular form
    print("Function parse_trade_intet called!")    
    return {"trade_state": trade_state, "item": item, "quantity": quantity}


def trade_consent(confirmation_prompt: str, player_response: str) -> dict:
    """
    Prüft, ob die Antwort des Spielers eine klare Zustimmung oder Ablehnung ist.
    Gibt 'yes', 'no' oder 'unsure' zurück.
    """
    print("Consent Tool")
    # Normalisieren
    response = player_response.lower().strip()

    # Klare Zustimmung
    consent_yes = ["yes", "sure", "okay", "alright", "let's do it", "absolutely", "of course", "ja", "klar", "mach ich", "mach mal", "auf jeden fall"]
    if any(phrase in response for phrase in consent_yes):
        return { "consent": "yes" }

    # Klare Ablehnung
    consent_no = ["no", "never mind", "i changed my mind", "nah", "nein", "doch nicht", "vergiss es", "nö"]
    if any(phrase in response for phrase in consent_no):
        return { "consent": "no" }

    # Vage oder verändert
    unclear_phrases = ["maybe", "not sure", "can i", "what about", "how about", "only if", "if you", "was kostet", "kann ich", "nur zwei", "hast du"]
    if any(phrase in response for phrase in unclear_phrases):
        return { "consent": "unsure" }

    # Wenn nichts eindeutig erkannt wurde
    return { "consent": "unsure" }



tool_parse = [
    {
        "type": "function",
        "name": "parse_trade_intent",
        "description": (
            "Analyze the player's message to determine if they express a clear intent to trade. "
            "If so, extract whether the intent is to 'buy' or 'sell', and also extract the item and quantity if mentioned. "
            "Only return a trade intent if the message clearly states the player wants to buy or sell a specific item. "
            "Do not return a trade intent for vague or exploratory questions like 'Do you have apples to sell?', "
                "'Can I buy some rum?', or 'I want to buy something'. In such cases, return 'no trade'.\n\n"
            "The result must always be returned as a JSON object with the following keys:\n"
            "- trade_state: either 'buy', 'sell', or 'no trade'\n"
            "- item: the name of the item (in singular form), or null if not specified\n"
            "- quantity: a positive integer, or 0 if for vague expressions like 'some apples', 'a lot of beer', or 'a few swords'."

        ),
        "parameters": {
            "type": "object",
            "properties": {
                "trade_state": {
                    "type": "string",
                    "description": "The player's trade intent: either 'buy', 'sell', or 'no trade'.",
                    "enum": ["buy", "sell", "no trade"]
                },
                "item": {
                    "type": ["string", "null"],
                    "description": "The item being bought or sold, in singular form. Null if no item is mentioned."
                },
                "quantity": {
                    "type": "integer",
                    "description": "The quantity of the item. Defaults to 1 if not specified.",
                    "minimum": 1
                }
            },
            "required": ["trade_state", "item", "quantity"],
            "additionalProperties": False
        }
    }
]

tool_consent = [
    {
        'type': 'function',
        'name': 'trade_consent',
        'description': (
            "Check whether the player's response to a trade confirmation question expresses clear consent to proceed with the trade. "
            "Return 'yes' if the player clearly agrees to the trade (e.g., 'Yes', 'Sure', 'Let's do it'). "
            "Return 'no' if the player refuses (e.g., 'No', 'I changed my mind'). "
            "Return 'unsure' if the message is unclear, evasive, or introduces changes (e.g., 'Maybe', 'Can I get only 2 instead?', 'What about pears?')."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'confirmation_prompt': {
                    'type': 'string',
                    'description': 'The confirmation message shown to the player (e.g. "Do you want to buy 3 apples?")'
                },
                'player_response': {
                    'type': 'string',
                    'description': 'The player\'s reply to the confirmation message.'
                }
            },
            'required': ['confirmation_prompt', 'player_response'],
            'additionalProperties': False
        }
    }
]



"""
# Define functional wrappers
def has_item_tool(input_text: str) -> str:
    item, quantity = parse_item_and_quantity(input_text)
    result = inventory.has_item(item, quantity)
    return (
        f"Yes, the NPC has at least {quantity} '{item}'."
        if result else
        f"No, the NPC does not have {quantity} '{item}'."
    )


def give_item_tool(input_text: str) -> str:
    item, quantity = parse_item_and_quantity(input_text)
    if inventory.has_item(item, quantity):
        inventory.remove_item(item, quantity)
        return f"The NPC gave away {quantity} '{item}'."
    else:
        return f"The NPC cannot give {quantity} '{item}' because it is not available."


def add_item_tool(input_text: str) -> str:
    item, quantity = parse_item_and_quantity(input_text)
    inventory.add_item(item, quantity)
    return f"The NPC received {quantity} '{item}'."


def list_inventory_tool(_: str = "") -> str:
    items = inventory.get_all_items()
    if not items:
        return "The NPC inventory is empty."
    return "NPC Inventory:\n" + "\n".join([f"- {item} (x{qty})" for item, qty in items])

"""