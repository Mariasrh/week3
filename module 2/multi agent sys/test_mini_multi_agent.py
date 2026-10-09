import sys
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- 1. Base Tools ---
@tool
def multiply_tool(a: int, b: int) -> int:
    """Multiplies two integers."""
    return a * b

@tool
def translate_to_spanish_tool(text: str) -> str:
    """Translates a given text string into Spanish."""
    return f"[Spanish] {text}"

# --- 2. Model Initialization ---
model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

# --- 3. Sub-Agents ---
math_sub_agent = create_agent(
    model=model,
    tools=[multiply_tool],
    system_prompt="You are a specialist in mathematical calculations."
)

spanish_sub_agent = create_agent(
    model=model,
    tools=[translate_to_spanish_tool],
    system_prompt="You are a specialist in Spanish translation."
)

# --- 4. Sub-Agents Wrapped as Tools for Supervisor ---
@tool
async def math_expert_agent(query: str) -> str:
    """Expert agent for solving mathematical calculations and word problems."""
    response = await math_sub_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return response["messages"][-1].content

@tool
async def spanish_expert_agent(query: str) -> str:
    """Expert agent for translating English text into Spanish."""
    response = await spanish_sub_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return response["messages"][-1].content

# --- 5. Supervisor Agent ---
supervisor_agent = create_agent(
    model=model,
    tools=[math_expert_agent, spanish_expert_agent],
    system_prompt="You are the supervisor agent. Delegate each task to the appropriate expert agent."
)

# --- 6. Execution and Output ---
async def main():
    print("=== MULTI-AGENT SUPERVISOR EXECUTION ===")
    query = "Calculate 12 times 12, then translate the result 'The result is 144' into Spanish."
    
    response = await supervisor_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    
    print("\n--- Final Supervisor Print Output ---")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())