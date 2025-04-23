import os
import chromadb
import uuid
from datetime import datetime
from openai import OpenAI


# Creating a persistent Client
client = chromadb.PersistentClient(path="vectordb")

# Creates the collecting if not yet exists or get the collection from the client
collection = client.get_or_create_collection(name="test_collection2")

def add_memory(text, role):
    """
    Adds the NPC-Answer to the database.
    :param text: the answer that is displayed to the user from OpenAi Api or the user prompt
    :param role: 'user' or 'assistant'
    :return: None
    """
    id = str(uuid.uuid4())
    collection.add(
        documents=[text],
        metadatas=[{"created": str(datetime.now()), "role": f"{role}"}],
        ids=[id]
    )
    print("added to memory")


def get_memory_user(text):
    results = collection.query(
        query_texts=[text],
        n_results=10,
        where={"role": "user"}
    )
    return results["documents"][0]


def get_memory_assistant(text):
    results = collection.query(
        query_texts=[text],
        n_results=10,
        where={"role": "assistant"}
    )
    return results["documents"][0]



# Initalize OpenAi
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Embedding model
#embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
#index = pc.Index(INDEX_NAME)
#print(embeddings)

