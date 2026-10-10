import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment key
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
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

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

memory = MemorySaver()

async def run_authenticated_agent(input_state: dict, config: dict):
    state = memory.get(config)
    messages = []
    
    if state and "messages" in state.get("channel_values", {}):
        messages = state["channel_values"]["messages"]
    elif input_state and "messages" in input_state:
        messages = input_state["messages"]

    # Strict check for authentication status across the full history
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
        interrupt_list = ["tools"]
    else:
        system_prompt = (
            "You are a strict security doorman. "
            "The user MUST authenticate first using the authenticate tool. "
            "Do not call any other function."
        )
        tools = [authenticate]
        interrupt_list = None

    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=memory,
        system_prompt=system_prompt,
        interrupt_before=interrupt_list
    )

    return await agent.ainvoke(input_state, config=config)

async def main_chat():
    config = {"configurable": {"thread_id": "user_chat_session"}}
    print("==================================================")
    print(" SECURE EMAIL AGENT CHAT (Type 'exit' to quit)")
    print("==================================================")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower().strip() in ["exit", "quit"]:
            print("Exiting chat session.")
            break

        res = await run_authenticated_agent({"messages": [HumanMessage(content=user_input)]}, config)
        
        state = memory.get(config)
        last_msg = state['channel_values']['messages'][-1]

        # Tool resolution loop
        while hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
            tool_call = last_msg.tool_calls[0]

            # Human-In-The-Loop interruption on send_email
            if tool_call['name'] == 'send_email':
                print(f"\n[HITL APPROVAL REQUIRED]")
                print(f"Action: Proposed email to '{tool_call['args'].get('recipient')}'")
                print(f"Subject: '{tool_call['args'].get('subject')}'")
                print(f"Body: '{tool_call['args'].get('body')}'")
                
                approval = input("Approve sending this email? (yes/no): ").strip().lower()
                if approval in ["yes", "y"]:
                    print("Executing send_email...")
                    res = await run_authenticated_agent(None, config)
                else:
                    print("Email sending cancelled by user.")
                    break
            else:
                # Automatic execution of safe tools (authenticate, read_inbox)
                res = await run_authenticated_agent(None, config)

            state = memory.get(config)
            last_msg = state['channel_values']['messages'][-1]

        if hasattr(last_msg, 'content') and last_msg.content:
            print(f"Agent: {last_msg.content}")

if __name__ == "__main__":
    asyncio.run(main_chat())