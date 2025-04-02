from npc_memory import NPCMemory
from npc_inventory import NPCInventory
from npc_controller import NPCController
import time
import os
from dotenv import load_dotenv

import openai

#Keys einfügen
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_KEY")

openai.api_key = OPENAI_KEY

response = openai.models.list()
print(response)


# 1.Initialisierung
memory = NPCMemory(
    pinecone_key=PINECONE_KEY,
    index_name="npc-core-test"
)

inventory = NPCInventory(db_path="test_npc_inventory.db")
npc = NPCController(memory, inventory)

# 2.Inventar-Test
print("\n--- INVENTAR TEST ---")
inventory.add_item("Heiltrank", 2)
inventory.add_item("Goldmünze", 10)

print("Hat Trank?", inventory.has_item("Heiltrank"))
print("Hat Schwert?", inventory.has_item("Schwert"))
print("Alle Items:", inventory.get_all_items())

# 3.Memory-Test
print("\n--- MEMORY TEST ---")
test_text = "Ich habe dem Spieler einen Trank versprochen."
memory.save_memory(test_text, role="npc", session_id="test-session")

# Kurze Pause, falls Pinecone asynchron schreibt
time.sleep(1)

similar = memory.search_memory("Habe ich dir schon einen Trank gegeben?")
print("Erinnerungen zur Trankfrage:")
for match in similar:
    print(f"- {match['metadata']['text']} ({match['score']:.2f})")

# 4.NPC-Logik-Test
print("\n--- NPC CONTROLLER TEST ---")
response = npc.process_request("Hast du noch einen Trank für mich?")
print("Antwort:", response)

response2 = npc.process_request("Hast du ein Schwert?")
print("Antwort:", response2)

response3 = npc.process_request("Was ist dein Lieblingsort?")
print("Antwort:", response3)
