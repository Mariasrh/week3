import sys
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

# Load environment variables
load_dotenv()

# Fix event loop policy for Windows OS
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Base LLM model
base_model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

# Global flag to control middleware behavior
purge_active = False

# Custom Model Wrapper that acts as a before-model middleware
class FilteredChatGroq:
    def __init__(self, model):
        self.model = model

    def bind_tools(self, tools, **kwargs):
        return FilteredChatGroq(self.model.bind_tools(tools, **kwargs))

    async def ainvoke(self, input_data, config=None, **kwargs):
        global purge_active
        if purge_active:
            # Extract messages list from input
            if isinstance(input_data, dict) and "messages" in input_data:
                filtered_msgs = []
                for msg in input_data["messages"]:
                    if isinstance(msg, ToolMessage):
                        continue
                    if isinstance(msg, AIMessage) and ("42.5" in str(msg.content) or getattr(msg, "tool_calls", None)):
                        continue
                    filtered_msgs.append(msg)
                input_data["messages"] = filtered_msgs
            elif isinstance(input_data, list):
                filtered_msgs = []
                for msg in input_data:
                    if isinstance(msg, ToolMessage):
                        continue
                    if isinstance(msg, AIMessage) and ("42.5" in str(msg.content) or getattr(msg, "tool_calls", None)):
                        continue
                    filtered_msgs.append(msg)
                input_data = filtered_msgs

        return await self.model.ainvoke(input_data, config=config, **kwargs)

    def __getattr__(self, name):
        return getattr(self.model, name)

# Wrap the model with middleware capabilities
model = FilteredChatGroq(base_model)

# Ephemeral data tool
@tool
def get_secret_temperature(city: str) -> str:
    """Returns the exact recorded temperature for a given city."""
    return f"The exact recorded temperature in {city} is 42.5°C."

# Initialize Memory Checkpointer
memory = MemorySaver()

# Create agent
agent = create_agent(
    model=model,
    tools=[get_secret_temperature],
    checkpointer=memory,
    system_prompt="You are a helpful assistant. Use tools when needed to answer questions."
)

# Helper function to print token counts
def print_token_stats(response_message, label=""):
    meta = getattr(response_message, "response_metadata", {})
    token_usage = meta.get("token_usage", {})
    prompt_tokens = token_usage.get("prompt_tokens", "N/A")
    completion_tokens = token_usage.get("completion_tokens", "N/A")
    total_tokens = token_usage.get("total_tokens", "N/A")
    
    print(f"   [Token Usage - {label}] Prompt: {prompt_tokens} | Completion: {completion_tokens} | Total: {total_tokens}")

# Main execution function
async def run_middleware_test():
    global purge_active
    config = {"configurable": {"thread_id": "session_memory_middleware_test"}}

    print("==================================================")
    print(" TASK 1: Long Conversation & Initial State ")
    print("==================================================")
    
    filler_prompts = [
        "Tell me a short fun fact about space.",
        "What is the capital of France?",
        "What is the exact secret temperature in Florence right now?"
    ]

    for idx, prompt in enumerate(filler_prompts, start=1):
        print(f"\nUser [{idx}]: {prompt}")
        res = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]}, config=config)
        last_msg = res["messages"][-1]
        print(f"Agent [{idx}]: {last_msg.content}")
        print_token_stats(last_msg, f"Run {idx}")

    state_before = memory.get(config)
    msgs_before = state_before["channel_values"]["messages"]
    print(f"\n📊 Total messages stored in memory checkpointer: {len(msgs_before)}")

    print("\n==================================================")
    print(" TASK 2: Enabling Before-Model Filtering Middleware ")
    print("==================================================")

    # Activate middleware filtering
    purge_active = True
    print("✅ Activated middleware filter to intercept messages before model invocation.")

    print("\n==================================================")
    print(" TASK 3: Proof Test & Token Count Comparison ")
    print("==================================================")

    test_prompt = "What was the exact numerical value of the temperature returned by the tool earlier?"
    print(f"User: {test_prompt}\n")

    res_test = await agent.ainvoke({"messages": [HumanMessage(content=test_prompt)]}, config=config)
    last_test_msg = res_test["messages"][-1]

    print(f"Agent Response:\n{last_test_msg.content}\n")
    print_token_stats(last_test_msg, "Post-Middleware Test Run")

if __name__ == "__main__":
    asyncio.run(run_middleware_test())