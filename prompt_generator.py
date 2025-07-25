#--------------------------------------------------------------------------------------
# prompt_generator.py – Builds prompt logic and context for NPC conversations
#--------------------------------------------------------------------------------------

import re
from typing import List, Dict
from inventory_store import get_all_items, get_entity_name, get_entity_role
from memory_store import format_chat_history_as_json, get_recent_chat_messages


#--------------------------------------------------------------------------------------
# Build role-specific instruction prompt for the LLM
#--------------------------------------------------------------------------------------

def build_instructions(id=1): # id hardcoded for now, will be changed to dynamic later
    """
    Returns a string of system-level instructions defining the NPC's name, role, and behavior.
    """
    npc_name = get_entity_name(id)
    npc_role = get_entity_role(id)
    prompt = f"""
        Your name is {npc_name} and you are an NPC in a role-playing game with that role: {npc_role}. 
        You have a good memory and remember past conversations or important information. 
        Use the memories only if you decide that it is necessary to provide accurate context.
        Always check to use the tools if the player is asking for something.
        You are in an ongoing conversation with a player—stay completely in character according to your assigned role and background.
        Never explain your reasoning or break the fourth wall.
        Respond in plain text only.
        Do not use emojis, symbols, or special Unicode characters.
        Avoid any non-verbal expressions like 😊, 🌀, etc.
    """
    return prompt.strip()


#--------------------------------------------------------------------------------------
# Build initial prompt using chat history and inventory
#--------------------------------------------------------------------------------------

def build_prompt(player_input):
    """
    Creates a prompt including chat memory and NPC inventory, formatted for OpenAI input.
    """

    # Uncomment if ChromaDB is enabled (semantic chat history, still in testing phase)
    """
    memories_player = get_memories_from_player(player_input)
    memories_npc = get_memories_from_npc(player_input)

    formatted_memories_player = "\n".join(f"- {m}" for m in memories_player)
    formatted_memories_npc = "\n".join(f"- {m}" for m in memories_npc)
    """

    chat_history_json = format_chat_history_as_json(limit=20)
    inventory_npc = get_all_items(1) # id hardcoded for now, will be changed to dynamic later

    prompt = f"""
        This is your latest chat history with the player. Use this as memory and for context.
        {chat_history_json}

        These are the items you currently have to sell:
        {inventory_npc}

        Your goals are:
        - Engage naturally and relevantly with the player
        - Offer items from your inventory based on expressed needs or interests
        - Only suggest what you actually have and in available quantity

        Use tools when appropriate:
        - Use 'parse_trade_intent' if the player clearly expresses a desire to buy or sell a specific item.
        - Use 'trade_consent' only after you've asked for trade confirmation and the player responds.

        Never guess items. Do not trigger tools preemptively or on vague or ambiguous requests.

        Now the player is speaking to you. Respond appropriately, naturally, and in character.

        Player says: "{player_input}"
    """
    return prompt.strip()


#--------------------------------------------------------------------------------------
# Build follow-up confirmation prompt after a trade tool call
#--------------------------------------------------------------------------------------

def build_followup_prompt(buy_items, sell_items):
    """
    Builds a prompt to ask the player to confirm trade actions previously parsed.
    """
    chat_history_followup = get_recent_chat_messages(limit=6)

    prompt = f"""
        The player has expressed an intent to buy {buy_items} and sell {sell_items}.
        Ask the player to confirm this trade. If ether buy or sell is empty, do not ask for confirmation of the empty one. 
        If both are empty, do not ask for confirmation. If there are many items, ask for confirmation for each item.

        This is the recent conversation with the player. Use it to determine the context about what the player asked for.
        {chat_history_followup}

        Make sure to:
        - Ask the question clearly, such as: 'Are you sure you want to buy 5 apples and sell 2 swords? Let's make a deal!'
    """
    return prompt.strip()


#--------------------------------------------------------------------------------------
# Infer trade intent heuristically from recent chat messages (still in testing phase)
#--------------------------------------------------------------------------------------

def infer_trade_items(inventory: Dict[str, int]) -> Dict[str, int]:
    """
    Tries to infer desired trade items and quantities based on recent chat input.
    Only returns items found in inventory.
    """
    chat_history = get_recent_chat_messages(limit=2)
    inferred = {}

    # Use the last relevant sentence
    lines = [line.strip().lower() for line in chat_history.strip().splitlines() if line.strip()]
    if not lines:
        return {}

    last_player_line = ""
    for line in reversed(lines):
        if line.startswith("player:") or line.startswith("you:"):
            last_player_line = line.split(":", 1)[-1].strip()
            print(f"This is last PlayerLine: {last_player_line}")
            break

    # Keywords like "all", "everything", "some"
    if any(word in last_player_line for word in ["all", "everything", "whatever"]):
        return {item: quantity for item, quantity in inventory.items() if quantity > 0}

    # Looking for quantities and items
    for item in inventory:
        # Allow variants like "5 apples", "five apples", "give me 2 apples"
        pattern = rf"(\\d+)\\s+{item}"
        match = re.search(pattern, last_player_line)
        if match:
            quantity = int(match.group(1))
            available_quantity = inventory[item]
            inferred[item] = min(quantity, available_quantity)

    # If quantity is unclear but item is matched -> offer max item
    if not inferred:
        for item in inventory:
            if item in last_player_line and inventory[item] > 0:
                inferred[item] = inventory[item]

    return inferred

