from inventory_store import get_all_items, get_entity_name, get_entity_role
from memory_store import get_memories_from_player, get_memories_from_npc, get_recent_chat_messages


def build_instructions(id=1):
    npc_name = get_entity_name(id)
    npc_role = get_entity_role(id)
    prompt = f"""
        Your name is {npc_name} and you are an NPC in a role-playing game with that role: {npc_role}. 
        You have a good memory and remember past conversations or important information. 
        Use the memories only if you decide that it is necessary to provide accurate context.
        Always check to use the tools if the player is asking for something.
        You are in an ongoing conversation with a player—stay completely in character according to your assigned role and background.
        Never explain your reasoning or break the fourth wall.
        """
    return prompt.strip()


def build_prompt(player_input):
    memories_player = get_memories_from_player(player_input)
    memories_npc = get_memories_from_npc(player_input)

    formatted_memories_player = "\n".join(f"- {m}" for m in memories_player)
    print(formatted_memories_player)
    formatted_memories_npc = "\n".join(f"- {m}" for m in memories_npc)
    print(formatted_memories_npc)
    formatted_chat_history = get_recent_chat_messages(limit=20)
    print(formatted_chat_history)

    inventory_npc = get_all_items(1)

    prompt = f"""
        These are your memories of what the player has told you somewhere in the past:
        {formatted_memories_player}

        These are your memories of what you have told the player somewhere in the past:
        {formatted_memories_npc}

        These are the items you currently have to sell:
        {inventory_npc}

        Guidelines for trading:
        - Offer items selectively, not all at once. Stay within the limits of your inventory.
        - Base your offers on the player's current behavior, interests, and needs expressed in the conversation.
        - Suggest items if they match the player's situation, but do not overwhelm the player with too many options.
        - If the player does not have enough money, suggest items that are affordable.
        - Never trigger the tool 'parse_trade_items' for invalid or impossible trades.
        Invalid means: items not present in your inventory, or quantities that exceed what you have.
        - Instead, respond in character, informing the player what is actually available.
        - Only use 'parse_trade_items' if the player's request matches the available items and quantities.
        - If the player's request is ambiguous or vague (e.g., 'I want them all', 'give me some', 'I will take whatever'), 
        do not trigger the tool 'parse_trade_items' instead ask the player to be more specific.
        - Always ensure that your inference is grounded in the chat context and your current inventory. Never guess items you don't offer.


        This is your recent conversation with the player:
        {formatted_chat_history}0

        Now the player is speaking to you. Respond appropriately, naturally, and in character.
        Use your memories if they help you better understand the player or the situation and if they are relevant to the conversation.
        Use the chat history to understand the player's current situation and needs and to construct context for your response.

        Player says: "{player_input}"
        """
    return prompt.strip()


def build_followup_prompt(buy_items, sell_items):  
    prompt = f"""
        The player has expressed an intent to buy {buy_items} and sell {sell_items}.
        Ask the player to confirm this trade. If ether buy or sell is empty, do not ask for confirmation of the empty one. 
        If both are empty, do not ask for confirmation. If there are many items, ask for confirmation for each item.

        Once the player responds, use the tool 'trade_consent' to determine whether they clearly consent to the trade.
        Do not proceed with the trade unless consent is 'yes'.

        Make sure to:
        - Ask the question clearly, such as: 'Are you sure you want to buy 5 apples and sell 2 swords? Let's make a deal!'
        - Only trigger the tool once the player responds.
        - If the player's answer is unclear, indirect, or they change the terms, the tool should return 'unsure'.

        Always call the tool with:
        - confirmation_prompt: the exact question you asked
        - player_response: the response message from the player
    """
    return prompt.strip()


