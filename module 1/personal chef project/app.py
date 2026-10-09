import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

load_dotenv()

st.set_page_config(
    page_title="AI Chef",
    page_icon="👨‍🍳",
    layout="centered"
)

st.title("👨‍🍳 Assistant Chef")
st.caption("Provide your remaining ingredients and let the Chef find recipes for you!")

def safe_search(query: str) -> str:
    try:
        ddg = DuckDuckGoSearchRun()
        return ddg.run(query)
    except Exception as e:
        return (
            "Web search error (network or DNS issue). "
            "Ignore the tool and use your own culinary knowledge to answer."
        )

search_tool = Tool(
    name="duckduckgo_search",
    description="Search for recipe ideas on the web.",
    func=safe_search
)

# Initialisation directe de l'agent
if "agent" not in st.session_state:
    tools = [search_tool]
    system_prompt = (
        "You are a creative and pragmatic chef. "
        "The user will give you a list of ingredients they have left in their kitchen. "
        "Use the web search tool to find suitable recipes. "
        "If the web search fails or returns an error message, use your own "
        "knowledge directly to suggest great, practical recipes."
    )
    model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.7)
    checkpointer = MemorySaver()
    st.session_state.agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt,
        checkpointer=checkpointer
    )

agent = st.session_state.agent

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "session_streamlit_1"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("E.g., I have chicken, rice, and carrots..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.chat_message("assistant"):
        with st.spinner("The Chef is thinking and searching for recipes..."):
            response = agent.invoke(
                {"messages": [("user", user_input)]},
                config=config
            )
            bot_response = response["messages"][-1].content
            st.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})