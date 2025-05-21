# Initialize database
inventory = NPCInventory(db_path="npc_inventory.db")


def parse_item_and_quantity(text: str):
    if not text or not text.strip():
        raise ValueError("Input cannot be empty")
    
    parts = text.split()
    item = parts[0].strip()
    if not item:
        raise ValueError("Item name cannot be empty")
    
    # Handle plural forms
    item = item.lower()  # Convert to lowercase for consistency
    if item.endswith('s'):
        item = item[:-1]  # Remove trailing 's' for singular form
        
    quantity = 1
    if len(parts) > 1:
        try:
            quantity = int(parts[1].strip())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            raise ValueError("Quantity must be a valid positive number")

    return {"item": item, "quantity": quantity}


tools = [
    {
        "type": "function",
        "name": "parse_item_and_quantity",
        "description": (
            "Extracts an item and quantity from input. Format must be 'item quantity', "
            "such as 'apple 5', 'rum 1' or 'banana 2'. Quantity must be an integer. "
            "Always use singular form for the item. Do not use words for numbers."
            "If no specific quantity is given, set it to 1."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": (
                        "A phrase containing the item and numeric quantity, like 'apple 5' or 'bread 2'. "
                        "Always provide the quantity as a number. Do not use words like 'five' or 'some'."
                    )
                }
            },
            "required": ["text"],
            "additionalProperties": False
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