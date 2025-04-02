import os
import openai
import pinecone
from dotenv import load_dotenv
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from test_npc_core import memory

# Setup environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "npc-langchain-memory"

# Initalize OpenAi and Pinecone
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Embedding model
embedding = OpenAIEmbeddings(opanai_api_key=OPENAI_API_KEY)

# Create index if it does not exist
if INDEX_NAME not in pc.list_indexes():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east1'
        )
    )

# Connect to index
vectorstore = LangchainPinecone.from_existing_idex(
    index_name=INDEX_NAME,
    embedding=embedding
)

# Setup LangChain memory using retriever
memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    memory_key="chat_history"
)

# Exportable memory instance
def get_memory():
    return memory


