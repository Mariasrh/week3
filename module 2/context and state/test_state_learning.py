import sys
import asyncio
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.graph.message import add_messages
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 1. Define custom state schema with add_messages reducer
class CustomAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    learned_preference: str

# 2. Tool to update state channel and return required ToolMessage
@tool
def save_user_preference(
    preference: str, 
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Saves or updates a learned user preference in the state."""
    return Command(
        update={
            "learned_preference": preference,
            "messages": [
                ToolMessage(
                    content=f"Saved preference: {preference}",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )

async def test_state():
    print("--- Test 3: Agent learning and modifying State ---")
    model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)
    checkpointer = MemorySaver()
    
    agent = create_agent(
        model=model,
        tools=[save_user_preference],
        state_schema=CustomAgentState,
        checkpointer=checkpointer
    )
    
    config = {"configurable": {"thread_id": "session_state_demo"}}
    
    user_input = "Please note that I prefer concise answers without polite greetings."
    
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    
    print("\nAgent Response:")
    print(response["messages"][-1].content)
    
    # 3. Verify state mutation
    current_state = await agent.aget_state(config)
    print("\n[STATE VERIFICATION]:")
    print("Field 'learned_preference' =", current_state.values.get("learned_preference"))

if __name__ == "__main__":
    asyncio.run(test_state())