import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent
possible_env_paths = [
    current_dir / ".env",
    current_dir.parent / ".env",
    current_dir.parent.parent / ".env"
]

for env_path in possible_env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

if not os.getenv("GROQ_API_KEY"):
    print("ERROR: GROQ_API_KEY is missing. Please set it in your environment or .env file.")
    sys.exit(1)

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState, START, END

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=400)

SECRET_CONTEXT = {
    "valid_email": "admin@company.com",
    "valid_password": "SuperSecretPassword123"
}

@tool
def authenticate(email: str, password: str) -> str:
    """Authenticates the user with provided credentials."""
    if email == SECRET_CONTEXT["valid_email"] and password == SECRET_CONTEXT["valid_password"]:
        return "SUCCESS: User authenticated successfully. Email tools unlocked."
    return "FAILURE: Invalid credentials."

@tool
def read_inbox() -> str:
    """Reads incoming emails from the inbox."""
    return "Inbox: [Client Email] 'Please confirm the 15% discount for order 402.'"

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Sends an email (Sensitive action protected by HITL)."""
    return f"EMAIL SENT TO {recipient} | Subject: {subject} | Body: {body}"

# Dynamic agent node for LangGraph Studio / Agent Chat UI
async def dynamic_doorman_node(state: MessagesState):
    messages = state["messages"]
    
    is_authenticated = any(
        isinstance(msg, ToolMessage) and "SUCCESS:" in str(msg.content)
        for msg in messages
    )

    if is_authenticated:
        system_prompt = (
            "You are an authorized email assistant with access to two tools: read_inbox and send_email. "
            "Use read_inbox to check emails and send_email to send or reply to messages."
        )
        tools = [read_inbox, send_email]
    else:
        system_prompt = (
            "You are a strict security doorman. "
            "The user MUST authenticate first using the authenticate tool. "
            "Do not call any other function."
        )
        tools = [authenticate]

    sub_agent = create_react_agent(model=model, tools=tools, prompt=system_prompt)
    result = await sub_agent.ainvoke({"messages": messages})
    return {"messages": result["messages"]}

# Build the main graph exported to langgraph.json
workflow = StateGraph(MessagesState)
workflow.add_node("doorman_agent", dynamic_doorman_node)
workflow.add_edge(START, "doorman_agent")
workflow.add_edge("doorman_agent", END)

# IMPORTANT: Remove checkpointer here as LangGraph Studio handles it automatically
graph = workflow.compile(
    interrupt_before=["doorman_agent"]
)