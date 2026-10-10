import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialize LLM
model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=300)

# Tool Definitions 
@tool
def read_inbox() -> str:
    """Reads incoming emails (AUTOMATIC - Read-only low risk action)."""
    return "Received email from client@example.com: 'Please confirm the pricing for 80 guests on June 15th.'"

@tool
def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Sends an email (GATED - Sensitive action requiring human approval)."""
    return f"✅ EMAIL SENT TO {recipient} | Subject: {subject} | Body: {body}"

memory = MemorySaver()

# Interrupt before the 'tools' node
agent = create_agent(
    model=model,
    tools=[read_inbox, send_email_tool],
    checkpointer=memory,
    system_prompt="You are an automated email assistant. First use read_inbox to check messages, then use send_email_tool to send the requested confirmation.",
    interrupt_before=["tools"]
)

async def test_response_mode(mode: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n==================================================")
    print(f" TESTING RESPONSE MODE: {mode.upper()}")
    print(f"==================================================")
    
    prompt = "Read my inbox, then send an email to client@example.com confirming the rate of €4,500."
    
    # First execution pass
    async for _ in agent.astream({"messages": [HumanMessage(content=prompt)]}, config=config):
        pass

    state = memory.get(config)
    last_msg = state['channel_values']['messages'][-1]

    # If read_inbox was called, automatically resume execution past the read-only step
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        if last_msg.tool_calls[0]['name'] == 'read_inbox':
            print(" Executing read-only tool 'read_inbox' automatically...")
            async for _ in agent.astream(None, config=config):
                pass
            state = memory.get(config)
            last_msg = state['channel_values']['messages'][-1]

    # Verify we are paused at send_email_tool
    if not (hasattr(last_msg, 'tool_calls') and last_msg.tool_calls):
        print(" Error: Agent did not trigger a tool call.")
        return

    tool_call = last_msg.tool_calls[0]
    print(f"⏸ Interrupted at gated tool boundary: {tool_call['name']}")
    print(f" Proposed arguments: {tool_call['args']}")

    #  Apply 3 Response Modes 
    if mode == "approve":
        print("\n Action: APPROVE (Proceed without modification)")
        async for _ in agent.astream(None, config=config):
            pass

    elif mode == "reject":
        print("\n Action: REJECT WITH REASON (Deny execution with feedback)")
        rejection_msg = ToolMessage(
            content="Action rejected by user: The €4,500 quote is incorrect. Do not send this email.",
            tool_call_id=tool_call['id']
        )
        agent.update_state(config, {"messages": [rejection_msg]}, as_node="tools")
        async for _ in agent.astream(None, config=config):
            pass

    elif mode == "edit":
        print("\n Action: EDIT (Directly modify proposed arguments)")
        edited_args = tool_call['args'].copy()
        edited_args['body'] = "Hello,\n\nI am pleased to confirm our firm quote of €4,200 for 80 guests on June 15th.\n\nBest regards,"
        last_msg.tool_calls[0]['args'] = edited_args
        
        human_note = HumanMessage(
            content="[HITL User Instruction]: The quoted rate was updated to €4,200 by the user for this send action."
        )
        agent.update_state(config, {"messages": [last_msg, human_note]})
        async for _ in agent.astream(None, config=config):
            pass

    final_state = memory.get(config)
    print(f"\n Final Agent Response:\n{final_state['channel_values']['messages'][-1].content}")

async def main():
    await test_response_mode("approve", "thread_1")
    
    print("\n Pause (10s delay)...")
    await asyncio.sleep(10)
    
    await test_response_mode("reject", "thread_2")
    
    print("\n Pause (10s delay)...")
    await asyncio.sleep(10)
    
    await test_response_mode("edit", "thread_3")

if __name__ == "__main__":
    asyncio.run(main())