import sys
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from context_schema import UserContext, get_user_context

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def test_success():
    print("--- Test 2: Invoke WITH context reading tool ---")
    model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)
    
    # Create agent WITH get_user_context tool
    agent = create_agent(model=model, tools=[get_user_context])
    
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
    
    print("\nAgent Response (SUCCESS):")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(test_success())