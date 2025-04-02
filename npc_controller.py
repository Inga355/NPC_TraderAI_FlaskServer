class NPCController:
    def __init__(self, memory, inventory):
        self.memory = memory
        self.inventory = inventory

    def respond_to_player(self, query):
        matches = self. memory.search_memory(query)
        print("Erinnerungen dazu:")
        for match in matches:
            print(f"- ({match['metadata']['role']}) {match['metadata']['text']}")

        #Beispiel Check
        if "apple" in query.lower():
            if self.inventory.has_item("apple"):
                print("I have an apple. You want it?")
            else:
                print("Sorry, no apples today!")