import openai
import pinecone
import uuid
from datetime import datetime
from app.py import API_KEY, PINECONE_KEY
from openai import api_key


class NPCMemory:
    def __init__(self, openai_key, pinecone_key, pinecone_env, index_name="npc-memory"):
        openai.api_key = API_KEY
        pinecone.init(api_key= PINECONE_KEY, environment=pinecone_env)

        self.index_name = index_name
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(index_name, dimension=1536)
        self.index = pinecone.Index(index_name)

    def embed_text(self, text):
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]

    def save_memory(self, text, role="npc", session_id="default"):
        vector = self.embed_text(text)
        self.index.upsert([(
                str(uuid.uuid4()),
                vector,
                {
                    "text": text,
                    "role": role,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        ])

    def search_memory(self, query, top_k=3):
        vector = self.embed_text(query)
        result = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return result["matches"]