from langchain.tools import Tool
from npc_inventory import NPCInventory


# Initialize database
inventory = NPCInventory(db_path="npc_inventory.db")


def parse_item_and_quantity(text: str):
    parts = text.split(",")
    item = parts[0].strip()
    quantity = int(parts[1].strip()) if len(parts) > 1 else 1
    return item, quantity


# Define functional wrappers
def has_item_tool(input_text: str) -> str:
    item, quantity = parse_item_and_quantity(input_text)
    result = inventory.has_item(item, quantity)
    return (
        f"Yes, the NPC has at least {quantity} '{item}'."
        if result else
        f"No, the NPC does not have {quantity} '{item}'."
    )


def give_item_tool(item_name: str) -> str:
    item, quantity = parse_item_and_quantity(input_text)
    if inventory.has_item(item, quantity):
        inventory.remove_item(item, quantity)
        return f"The NPC gave away {quantity} '{item}'."
    else:
        return f"The NPC cannot give {quantity} '{item}' because it is not available."


def list_inventory_tool(_: str = "") -> str:
    items = inventory.get_all_items()
    if not items:
        return "The NPC inventory is empty."
    return "NPC Inventory:\n" + "\n".join([f"- {item} (x{qty})" for item, qty in items])


# Define tool for LangChain
tools = [
    Tool(
        name="has_item",
        func=has_item_tool,
        description="Checks if the NPC has a specific item. Input should be the item name, like 'healing potion'."
    ),
    Tool(
        name="give_item",
        func=give_item_tool,
        description="Removes one of the specified item from the NPC inventory. Input is the item name."
    ),
    Tool(
        name="list_inventory",
        func=list_inventory_tool,
        description="Returns the full list of items the NPC currently holds."
    )
]