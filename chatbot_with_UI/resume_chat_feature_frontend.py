# import streamlit as st
# from backend import chatbot
# from langchain_core.messages import HumanMessage,AIMessage
# import uuid
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI



# #*************************************************************************************
# load_dotenv()
# model=ChatGoogleGenerativeAI(model='gemini-2.5-flash')


# # **************************Utility functions*****************************************

# def generate_thread_id():
#     thread_id=uuid.uuid4()
#     return thread_id

# def reset_chat():
#     thread_id=generate_thread_id()
#     st.session_state['thread_id']=thread_id
#     add_thread(thread_id)
#     st.session_state['message_history']=[]
    



# def load_conversation(thread_id):
#     state=chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
#     return state.values.get('messages',[])

# def add_thread(thread_id,title='New Chat'): #2nd change
#     if thread_id not in st.session_state['chat_threads']:
#         st.session_state['chat_threads'][thread_id]=title

# def generate_header(mssg):
#     prompt=f"Generate a short title for the following message in 4-5 words: {mssg}.only return the title without any additional text."
#     response=model.invoke(prompt)
#     return response.content

# # ************************************************************************************



# #********************Session setup***************************
# if 'message_history' not in st.session_state:
#     st.session_state['message_history']=[]

# if 'thread_id' not in  st.session_state:
#     st.session_state['thread_id']=generate_thread_id()


# if 'thread_history' not in st.session_state:
#     st.session_state['thread_history']=[]

# if 'chat_threads' not in st.session_state: #First change
#     st.session_state['chat_threads']={}

# add_thread(st.session_state['thread_id'])
# #*******************************************************************


# #********************Sidebar***************************
# st.sidebar.title("chatbot with Streamlit UI")
# if st.sidebar.button("New Conversation"):
#     reset_chat()


# st.sidebar.header("My Conversations")


# for thread,title in reversed(st.session_state['chat_threads'].items()):
#     #if st.sidebar.button(str(thread)):
#     if st.sidebar.button(title):
#         st.session_state['thread_id']=thread
#         messages=load_conversation(thread)
#         #load conversation history
#         temp_message=[]

#         for mssg in messages:
#             if isinstance(mssg,HumanMessage):
#                 role='user'
#             else:
#                 role='assistant'
#             temp_message.append({'role':role,'content':mssg.content})
        
#         st.session_state['message_history']=temp_message



# #*******************************************************************

# print(st.session_state['chat_threads'].items())




# #********************Displaying all the stored messages***************************
# for messg in st.session_state['message_history']:
#     with st.chat_message(messg['role']):
#         st.text(messg['content'])
# #*******************************************************************



# #***************************Main UI****************************************
# user_input=st.chat_input("Type here...")

# if user_input:
#     st.session_state['message_history'].append({'role':'user','content':user_input})
#     with st.chat_message('user'):
#         st.text(user_input)
    
#     #generate header for the chat thread if it is first message
#     if st.session_state['chat_threads'].get(st.session_state['thread_id'])=='New Chat':
#         title=generate_header(user_input)
#         st.session_state['chat_threads'][st.session_state['thread_id']]=title

    
#     config={'configurable':{'thread_id':st.session_state['thread_id']}}


#     #********************Use streaming for showing real time conversation feel***************************
#     with st.chat_message('assistant'):
#         def ai_only_stream():
#             for message_chunk,metadata in chatbot.stream(
#                 {'messages':[HumanMessage(content=user_input)]},
#                 config=config,
#                 stream_mode='messages'
#             ):
#                 if isinstance(message_chunk,AIMessage):
#                     yield message_chunk.content #yields only AI message content
#         ai_message=st.write_stream(ai_only_stream())


#     st.session_state['message_history'].append({'role':'assistant','content':ai_message})


import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load Environment and Model
load_dotenv()
model = ChatGoogleGenerativeAI(model='gemini-2.0-flash') # Updated to latest stable

# --- Page Config ---
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# Custom CSS for a cleaner sidebar
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #000000;
        color:#f0f2f6;
    }
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Utility Functions ---
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []
    st.rerun() # Forces UI to refresh cleanly

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def add_thread(thread_id, title='New Chat'):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'][thread_id] = title

def generate_header(mssg):
    prompt = f"Generate a short title (4-5 words max) for: {mssg}. Return only the title."
    response = model.invoke(prompt)
    return response.content.strip('"')

# --- Session State Initialization ---
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = {}

add_thread(st.session_state['thread_id'])

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 AI Chatbot")
    
    if st.button("➕ New Conversation", use_container_width=True):
        reset_chat()
    
    st.divider()
    st.subheader("History")
    
    # Render thread history as buttons
    for thread, title in reversed(list(st.session_state['chat_threads'].items())):
        # Highlight active thread
        type_style = "primary" if st.session_state['thread_id'] == thread else "secondary"
        
        if st.button(f"💬 {title}", key=thread, use_container_width=True, type=type_style):
            st.session_state['thread_id'] = thread
            messages = load_conversation(thread)
            
            temp_message=[]

            for mssg in messages:
               if isinstance(mssg,HumanMessage):
                role='user'
               else:
                role='assistant'
               temp_message.append({'role':role,'content':mssg.content})
        
            st.session_state['message_history']=temp_message
            

# --- Main Chat UI ---
st.title("Chat Interface")

# Display message history
for messg in st.session_state['message_history']:
    with st.chat_message(messg['role']):
        st.markdown(messg['content']) # Changed from st.text to st.markdown

# Chat Input
user_input = st.chat_input("Type your message here...")

if user_input:
    # 1. User Message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)
    
    # 2. Update Title if necessary
    if st.session_state['chat_threads'].get(st.session_state['thread_id']) == 'New Chat':
            new_title = generate_header(user_input)
            st.session_state['chat_threads'][st.session_state['thread_id']] = new_title
    
    # 3. Assistant Response (Streaming)
    with st.chat_message('assistant'):
        def ai_only_stream():
            config = {'configurable': {'thread_id': st.session_state['thread_id']}}
            for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=config,
                stream_mode='messages'
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    # 4. Save to history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})