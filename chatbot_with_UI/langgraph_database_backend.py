from langgraph.graph import StateGraph,START,END
from langchain_core.messages import HumanMessage,BaseMessage
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Annotated,TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

from langgraph.graph.message import add_messages
class chatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')

conn=sqlite3.connect('chatbot.db',check_same_thread=False)
checkpoint=SqliteSaver(conn=conn)

def chatNode(state:chatState):
    messages=state['messages']

    response=model.invoke(messages)
    return {'messages':[response]}

graph=StateGraph(chatState)

graph.add_node('chatNode',chatNode)

graph.add_edge(START,'chatNode')
graph.add_edge('chatNode',END)



chatbot=graph.compile(checkpointer=checkpoint)

def retrieve_all_threads():
    all_threads=set()
    for checkpoints in checkpoint.list(None):
        all_threads.add(checkpoints.config['configurable']['thread_id'])
    return list(all_threads)

