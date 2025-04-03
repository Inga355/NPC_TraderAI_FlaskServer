class NPCController:
    def __init__(self, memory, inventory):
        self.memory = memory
        self.inventory = inventory

    def respond_to_player(self, query):
        matches = self.memory.search_memory(query)
        print("Erinnerungen dazu:")
        for match in matches:
            print(f"- ({match['metadata']['role']}) {match['metadata']['text']}")

    def process_request(self, message):
        self.memory.save_memory(message, role="player")
        # Check auf Trank als Beispiel
        if "trank" in message.lower():
            if self.inventory.has_item("Heiltrank"):
                response = "Ich habe noch einen Trank für dich."
            else:
                response = "Leider habe ich keinen Trank mehr."
        else:
            # Fallback: relevante Erinnerungen suchen
            memories = self.memory.search_memory(message)
            if memories:
                response = f"Ich erinnere mich: {memories[0]['metadata']['text']}"
            else:
                response = "Ich bin mir nicht sicher, was du meinst."

        self.memory.save_memory(response, role="npc")
        return response

        #Beispiel Check
        if "apple" in query.lower():
            if self.inventory.has_item("apple"):
                print("I have an apple. You want it?")
            else:
                print("Sorry, no apples today!")