from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from memory_store import get_memory, memory
from agent_tools import tools
from dotenv import load_dotenv
import os


# Init LLM
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    temperature=0.7,
    open_api_key=OPENAI_API_KEY,
    model_name="gpt-4o-mini"
)

# Init memory from vector database
memory = get_memory()

# Init LangChain Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)

# Agent query interface
def ask_npc(prompt: str) -> str:
    try:
        response = agent.run(prompt)
        return response
    except Exception as e:
        return f"Something went wrong: {str(e)}"




