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

# Verify API key
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key or not groq_key.startswith("gsk_"):
    print("ERROR: GROQ_API_KEY is missing or invalid in your environment.")
    print("Please run: $env:GROQ_API_KEY='gsk_your_key_here'")
    sys.exit(1)

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Active models from Groq API
MODEL_CHEAP_NAME = "openai/gpt-oss-20b"
MODEL_CAPABLE_NAME = "qwen/qwen3.8-27b"

model_cheap = ChatGroq(model=MODEL_CHEAP_NAME, temperature=0, max_tokens=300)
model_capable = ChatGroq(model=MODEL_CAPABLE_NAME, temperature=0, max_tokens=300)

# Tool definitions
@tool
def web_search(query: str) -> str:
    """Public web search tool available to all users."""
    return f"Public result for '{query}': Information accessible to everyone."

@tool
def internal_db(query: str) -> str:
    """Internal database tool. Execute this tool to fetch requested internal HR or financial records."""
    return f"Confidential result for '{query}': Employee ID 104 details retrieved from internal database."

memory = MemorySaver()

def print_token_stats(response_message, label=""):
    meta = getattr(response_message, "response_metadata", {})
    token_usage = meta.get("token_usage", {})
    prompt_tokens = token_usage.get("prompt_tokens", "N/A")
    completion_tokens = token_usage.get("completion_tokens", "N/A")
    total_tokens = token_usage.get("total_tokens", "N/A")
    
    print(f"   [Token Usage - {label}] Prompt: {prompt_tokens} | Completion: {completion_tokens} | Total: {total_tokens}")

async def run_dynamic_agent(input_state: dict, config: dict):
    configurable = config.get("configurable", {})
    user_role = configurable.get("user_role", "external")
    user_lang = configurable.get("user_lang", "fr")
    messages = input_state.get("messages", [])
    
    # Task 1: Dynamic system prompt
    if user_lang == "es":
        system_prompt = "Eres un asistente servicial. Responde siempre en español."
    elif user_role == "internal":
        system_prompt = "You are an internal assistant. Execute the internal_db tool immediately whenever internal or HR queries are made."
    elif user_lang == "en":
        system_prompt = "You are a helpful assistant. Always answer in English."
    else:
        system_prompt = "Tu es un assistant utile. Réponds en français."

    # Task 2: Tool hiding by role (RBAC)
    if user_role == "internal":
        tools = [web_search, internal_db]
        selected_model = model_capable
        model_label = f"{MODEL_CAPABLE_NAME} (Capable Model - Internal)"
    else:
        tools = [web_search]
        selected_model = model_cheap
        model_label = f"{MODEL_CHEAP_NAME} (Cheap Model)"

    # Task 3: Dynamic model switching based on message history length
    msg_count = len(messages)
    if user_role != "internal":
        if msg_count > 10:
            selected_model = model_capable
            model_label = f"{MODEL_CAPABLE_NAME} (Capable Model)"
        else:
            selected_model = model_cheap
            model_label = f"{MODEL_CHEAP_NAME} (Cheap Model)"

    print(f"   [WRAP MIDDLEWARE] Messages: {msg_count} | Role: '{user_role}' | Language: '{user_lang}' | Model: {model_label}")

    agent = create_agent(
        model=selected_model,
        tools=tools,
        checkpointer=memory,
        system_prompt=system_prompt
    )
    
    return await agent.ainvoke(input_state, config=config)

async def run_tests():
    print("==================================================")
    print(" TASK 1: Dynamic Prompt (Language Switch)")
    print("==================================================")
    
    config_es = {"configurable": {"thread_id": "thread_lang", "user_lang": "es", "user_role": "external"}}
    res_es = await run_dynamic_agent({"messages": [HumanMessage(content="Bonjour, comment vas-tu ?")]}, config=config_es)
    last_msg_es = res_es['messages'][-1]
    print(f"Agent (Spanish): {last_msg_es.content}")
    print_token_stats(last_msg_es, "Task 1 Run")
    print()

    print("==================================================")
    print(" TASK 2: Tool Hiding by Role (RBAC)")
    print("==================================================")
    
    # External user execution
    config_ext = {"configurable": {"thread_id": "thread_ext", "user_lang": "en", "user_role": "external"}}
    print("External user attempt:")
    res_ext = await run_dynamic_agent({"messages": [HumanMessage(content="Search for employee ID 104 in the internal database.")]}, config=config_ext)
    last_msg_ext = res_ext['messages'][-1]
    print(f"Agent (External): {last_msg_ext.content}")
    print_token_stats(last_msg_ext, "External User Run")
    print()

    # Internal user execution
    config_int = {"configurable": {"thread_id": "thread_int", "user_lang": "en", "user_role": "internal"}}
    print("Internal user attempt:")
    res_int = await run_dynamic_agent({"messages": [HumanMessage(content="Search for employee ID 104 in the internal database.")]}, config=config_int)
    last_msg_int = res_int['messages'][-1]
    print(f"Agent (Internal): {last_msg_int.content}")
    print_token_stats(last_msg_int, "Internal User Run")
    print()

    print("==================================================")
    print(" TASK 3: Model Switch (> 10 Messages) & Token Comparison")
    print("==================================================")
    
    # Short conversation using cheap model
    config_short = {"configurable": {"thread_id": "thread_short", "user_lang": "en", "user_role": "external"}}
    print("Short conversation run:")
    res_short = await run_dynamic_agent({"messages": [HumanMessage(content="Give a short summary of solar power.")]}, config=config_short)
    last_msg_short = res_short['messages'][-1]
    print_token_stats(last_msg_short, "Cheap Model Run")
    print()

    # Long conversation using capable model
    config_long = {"configurable": {"thread_id": "thread_long", "user_lang": "en", "user_role": "external"}}
    dummy_history = []
    for i in range(11):
        dummy_history.append(HumanMessage(content=f"Question {i+1}"))
        dummy_history.append(AIMessage(content=f"Answer {i+1}"))
    
    dummy_history.append(HumanMessage(content="Give a short summary of solar power."))
    
    print("Long conversation run:")
    res_long = await run_dynamic_agent({"messages": dummy_history}, config=config_long)
    last_msg_long = res_long['messages'][-1]
    print_token_stats(last_msg_long, "Capable Model Run")

if __name__ == "__main__":
    asyncio.run(run_tests())