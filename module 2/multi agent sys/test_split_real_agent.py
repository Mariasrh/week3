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

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

# --- Sub-Agent: Data Research Specialist ---
@tool
def fetch_tech_specs(product_name: str) -> str:
    """Simulates looking up technical specifications for a product."""
    if "laptop" in product_name.lower():
        return "Laptop Specs: 16-core CPU, 32GB RAM, RTX 4080 GPU, 1TB SSD."
    return "Standard Product Specs: 8-core CPU, 8GB RAM, 256GB SSD."

research_sub_agent = create_agent(
    model=model,
    tools=[fetch_tech_specs],
    system_prompt="You are a technical research specialist. Your sole job is to fetch raw specifications."
)

@tool
async def research_specialist(query: str) -> str:
    """Specialist agent for retrieving technical product specifications."""
    res = await research_sub_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

# --- Supervisor: Copywriter & Coordinator ---
writer_supervisor = create_agent(
    model=model,
    tools=[research_specialist],
    system_prompt="You are a marketing copywriter. Request specifications from the research expert and draft an engaging product feature sheet."
)

async def main():
    print("=== REAL AGENT SPLIT TEST ===")
    response = await writer_supervisor.ainvoke({
        "messages": [HumanMessage(content="Write a marketing product sheet for the new Laptop Pro.")]
    })
    
    print("\n--- Final Draft Written by Supervisor ---")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())