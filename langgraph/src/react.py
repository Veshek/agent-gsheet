from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
import sqlite3
# In memory
from langgraph.checkpoint.sqlite import SqliteSaver
import os, getpass
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
conn = sqlite3.connect(":memory:", check_same_thread = False)

db_path = "state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)

memory = SqliteSaver(conn)

def findtable() -> str:
    """Finds the table in the CRM.
    """
    return "table1"

def getRow() -> list:
    """Retrieves a row from the table. given the user message.
    """
    return ["keshav", "kumar", "keshav@gmail.com"]

def addRow() -> str:
    """Adds Row to table
    """
    return "Row added successfully"

def deleteRow() -> str:
    """Deletes Row from table
    """
    return "Row deleted successfully"

tools = [findtable, getRow, addRow, deleteRow]

# Define LLM with bound tools
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content=
                        """
                        You are a helpful assistant tasked with assisting users with interacting with their CRM.
                        Users can ask you to add, view or delete records from their CRM. The flow that you will follow is to find the
                        table that the user is referring to, and then perform the required action on that table. You can also ask the user 
                        for more information if needed.
                        """)


class State(MessagesState):
    data: dict

# Node
def assistant(state: State):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Build graph
builder = StateGraph(State)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

# Compile graph
graph = builder.compile(checkpointer = memory)

config = {"configurable": {"thread_id": "1"}}

input_message = HumanMessage(content="What's my name?")
for chunk in graph.stream({"messages": [input_message]}, config,stream_mode="updates"):
    print(chunk['assistant']['messages'][-1].pretty_print())

for chunk in graph.stream({"messages": [HumanMessage(content="how's it going ?")]}, config, stream_mode="messages"):
    print(chunk)
        