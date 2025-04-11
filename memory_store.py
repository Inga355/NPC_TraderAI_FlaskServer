from openai import OpenAI
import os
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_openai import OpenAIEmbeddings
#from langchain_community.embeddings import OpenAIEmbeddings
from langchain.memory import VectorStoreRetrieverMemory
from dotenv import load_dotenv


# Setup environment
INDEX_NAME = "npc-langchain-memory"

# Initalize OpenAi and Pinecone
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
index = pc.Index(INDEX_NAME)
print(embeddings)

"""# Create index if it does not exist
if INDEX_NAME not in pc.list_indexes():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east1'
        )
    )"""

# Connect to index
vectorstore = LangchainPinecone(index, embedding=embeddings)

# Setup LangChain memory using retriever
memory = VectorStoreRetrieverMemory(
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    memory_key="chat_history"
)

# Exportable memory instance
def get_memory():
    return memory


