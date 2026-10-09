import sys
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

load_dotenv()

# EventLoop fix for Windows
if sys.platform == "win32":
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def main():
    # Multi-server MCP client setup
    client = MultiServerMCPClient({
        "small_server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-u", "my_small_server.py"]
        },
        "time_server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "mcp_server_time", "--local-timezone=Europe/Paris"]
        }
    })

    try:
        # Retrieve tools exposed by all connected MCP servers
        tools = await client.get_tools()
        print("Successfully loaded tools:", [t.name for t in tools])
    except Exception as e:
        print(f"Error retrieving tools: {e}")
        return

    # Initialize ChatGroq LLM
    model = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0
    )

    # Create the agent using langchain.agents.create_agent
    agent = create_agent(
        model=model,
        tools=tools
    )

    # TEST 1: LOCAL TOOL ONLY
    
    question_local = HumanMessage(content="Please add 1234 and 5678 together using your addition tool.")
    
    print("\n--- Running Test 1: Local Tool Only ---")
    response_local = await agent.ainvoke({"messages": [question_local]})
    print("Agent Response:\n", response_local["messages"][-1].content)

    # TEST 2: PUBLIC TIME TOOL ONLY
    question_time = HumanMessage(content="What is the current time in Paris right now?")
    
    print("\n--- Running Test 2: Public Time Tool Only ---")
    response_time = await agent.ainvoke({"messages": [question_time]})
    print("Agent Response:\n", response_time["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())