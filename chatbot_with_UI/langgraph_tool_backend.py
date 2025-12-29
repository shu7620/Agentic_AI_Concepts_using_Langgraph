from langgraph.graph import StateGraph,START,END
from langchain_core.messages import HumanMessage,BaseMessage
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated,TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition 
from langchain_community.tools import DuckDuckGoSearchRun
import requests

load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')

#-----Tools --------
search_tool=DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Advantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=Z51R1NVY0YGQ8PO7"
    r = requests.get(url)
    return r.json()

tools=[search_tool,calculator,get_stock_price]
model_with_tools=model.bind_tools(tools)


#--------------State------------------
from langgraph.graph.message import add_messages
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]


#--------------checkpointer----------------
conn=sqlite3.connect('chatbot.db',check_same_thread=False)
checkpoint=SqliteSaver(conn=conn)

#--------------Nodes----------------
def chatNode(state:chatState):
    """LLM node that may answer or request a tool call."""
    messages=state['messages']

    response=model_with_tools.invoke(messages)
    return {'messages':[response]}

tool_node=ToolNode(tools)

#--------------Graph----------------
graph=StateGraph(chatState)

graph.add_node('chat_Node',chatNode)
graph.add_node('tools',tool_node)

graph.add_edge(START,'chat_Node')
graph.add_conditional_edges('chat_Node',tools_condition)
graph.add_edge('tools','chat_Node')


chatbot=graph.compile(checkpointer=checkpoint)

def retrieve_all_threads():
    all_threads=set()
    for checkpoints in checkpoint.list(None):
        all_threads.add(checkpoints.config['configurable']['thread_id'])
    return list(all_threads)

