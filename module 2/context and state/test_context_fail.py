import sys
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from context_schema import UserContext

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_fail():
    print("--- Test 1: Invoke without context reading tool ---")
    model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)
    
    # Create agent WITHOUT get_user_context tool
    agent = create_agent(model=model, tools=[])
    
    config = {
        "configurable": {
            "thread_id": "1",
            "context": UserContext()
        }
    }
    
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content="What is my preferred language and role?")]},
        config=config
    )
    
    print("\nAgent Response (EXPECTED FAILURE):")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(test_fail())