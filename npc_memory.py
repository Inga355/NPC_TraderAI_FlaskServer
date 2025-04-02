import openai
from openai import OpenAI, api_key
from pinecone import Pinecone, ServerlessSpec
import uuid
from datetime import datetime, timezone
import os
from dotenv import load_dotenv


load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)


class NPCMemory:
    def __init__(self, pinecone_key, pinecone_env, index_name="npc-memory"):
        pc = Pinecone(api_key= pinecone_key)

        self.index_name = index_name
        if index_name not in pc.list_indexes().names():
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=pinecone_env
                )
            )
        self.index = pc.Index(index_name)

    def embed_text(self, text):
        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )
        embedding = response.data[0].embedding
        return embedding

    def save_memory(self, text, role="npc", session_id="default"):
        vector = self.embed_text(text)
        self.index.upsert([(
                str(uuid.uuid4()),
                vector,
                {
                    "text": text,
                    "role": role,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
        ])

    def search_memory(self, query, top_k=3):
        vector = self.embed_text(query)
        result = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return result["matches"]