#--------------------------------------------------------------------------------------
# agent_tools.py – Tool Definitions for Trade Intent and Consent Parsing
#--------------------------------------------------------------------------------------

def parse_trade_intent(trade_state: str="no trade", item: str="null", quantity: int=0):
    """
    Parses trade intent and normalizes item name.
    """
    item = item.lower()
    if item.endswith('s'):
        item = item[:-1]
    print("\033[92mFunction parse_trade_intet called!\033[0m")    
    return {"trade_state": trade_state, "item": item, "quantity": quantity}


def trade_consent(consent: str='unsure'):
    """
    Handles consent responses from player for trade confirmation.
    """
    print("\033[92mFunction trade_consent called!\033[0m")
    return {"Consent": consent}


#--------------------------------------------------------------------------------------
# Tool Definitions for OpenAI Function Calling
#--------------------------------------------------------------------------------------

tools = [ 
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
    },
    {
        'type': 'function',
        'name': 'trade_consent',
        "description": (
            "Analyze the most recent chat history to determine whether the player's message is a direct response "
            "to a trade confirmation question from the previous assistant message. "
            "Use this tool only if the last assistant message asked the player to confirm a specific trade. "
            "Return 'yes' if the player clearly agrees (e.g., 'Yes', 'Sure', 'Let's do it', 'deal', 'ok', or similiar phrases). "
            "Return 'no' if the player explicitly refuses (e.g., 'No', 'I changed my mind', 'not today' or similiar phrases). "
            "Return 'unsure' if the player's message is unclear, indirect, or changes the terms (e.g., 'Maybe', "
            "'Can I get only 2 instead?', 'What about pears?')."
        ),
        'parameters': {
            'type': 'object',
            'properties': {
                'consent': {
                    'type': 'string',
                    'description': "The players trade consent: either 'yes', 'no' or 'unsure'."
                },
            },
            'required': ['consent'],
            "additionalProperties": False
        }
    }
]