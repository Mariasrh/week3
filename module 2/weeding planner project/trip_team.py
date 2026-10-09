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

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=350)

# --- 1. Outils Voyage ---
@tool
def search_trip_flights(departure: str, arrival: str) -> str:
    """Finds flight routes for personal trips."""
    return f"Flights ({departure} -> {arrival}): Direct Flight ($190 A/R), Connecting Flight ($130 A/R)."

@tool
def search_hotels(city: str, budget_level: str) -> str:
    """Finds accommodation options matching budget preferences."""
    return f"Hotels in {city} ({budget_level}): Central Boutique Hotel ($120/night), Panoramic Residence ($85/night)."

@tool
def search_activities(city: str, interest: str) -> str:
    """Discovers local activities, sights, and culinary highlights."""
    return f"Activities in {city} ({interest}): Guided historical tour, Local food tasting, Museum pass."

# --- 2. Sous-Agents Voyage ---
trip_flight_agent = create_agent(model=model, tools=[search_trip_flights], system_prompt="You are a flight booking expert.")
hotel_agent = create_agent(model=model, tools=[search_hotels], system_prompt="You are an accommodation specialist.")
activity_agent = create_agent(model=model, tools=[search_activities], system_prompt="You are a local tour guide and activity expert.")

# --- 3. Sous-agents encapsulés en outils ---
@tool
async def trip_flight_specialist(query: str) -> str:
    """Consults the flight specialist."""
    res = await trip_flight_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

@tool
async def hotel_specialist(query: str) -> str:
    """Consults the accommodation specialist."""
    res = await hotel_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

@tool
async def activity_specialist(query: str) -> str:
    """Consults the activity specialist."""
    res = await activity_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

# --- 4. Trip Supervisor ---
trip_supervisor = create_agent(
    model=model,
    tools=[trip_flight_specialist, hotel_specialist, activity_specialist],
    system_prompt="You are an expert Personal Travel Advisor. Chat with the user to discover their needs and consult your specialists to build a concise itinerary."
)

async def run_trip_chat(user_message: str, history: list) -> str:
    messages = []
    
    # Prise en charge compatible Gradio 6.0+ (dicts ou tuples)
    for msg in history:
        if isinstance(msg, dict):
            if msg.get("role") == "user" and msg.get("content"):
                messages.append(HumanMessage(content=msg["content"]))
        elif isinstance(msg, (list, tuple)) and len(msg) == 2:
            if msg[0]:
                messages.append(HumanMessage(content=msg[0]))
                
    messages.append(HumanMessage(content=user_message))
    
    res = await trip_supervisor.ainvoke({"messages": messages})
    return res["messages"][-1].content