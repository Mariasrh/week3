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

# Modèle actif Groq avec limitation max_tokens pour respecter les quotas OTPM
model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=350)

# --- 1. Outils des sous-agents ---
@tool
def search_flights_tool(origin: str, destination: str, date: str) -> str:
    """Searches available flight options to the destination."""
    return f"Flights ({origin} -> {destination} on {date}): Air France AF102 ($450/p), EasyJet EJ88 ($280/p)."

@tool
def search_venues_tool(destination: str, capacity: int) -> str:
    """Searches wedding venues and private villas at the destination."""
    return f"Venues in {destination} ({capacity} guests): Villa Bella Vista ($4,500/day), Chateau Le Paradis ($6,200/day)."

@tool
def search_music_tool(genre: str) -> str:
    """Searches playlists and DJ packages based on preferred music genre."""
    return f"Music [{genre}]: Sunset Chill & Pop Hits Playlist (40 tracks), DJ Alex Live Package ($1,200)."

@tool
def generate_writing_tool(topic: str, tone: str) -> str:
    """Drafts wedding speeches, invitation messages, or vows."""
    return f"Drafted [{tone}] message for [{topic}]: 'We warmly invite you to join us in celebrating our wedding day filled with love!'"

# --- 2. Sous-Agents Spécialistes ---
travel_agent = create_agent(
    model=model, 
    tools=[search_flights_tool], 
    system_prompt="You are a travel agent specializing in luxury destination flights."
)

venue_agent = create_agent(
    model=model, 
    tools=[search_venues_tool], 
    system_prompt="You are a venue scout specializing in premier wedding locations."
)

dj_agent = create_agent(
    model=model, 
    tools=[search_music_tool], 
    system_prompt="You are an event DJ and musical director."
)

writer_agent = create_agent(
    model=model, 
    tools=[generate_writing_tool], 
    system_prompt="You are a creative writer specializing in wedding invitations, vows, and speeches."
)

# --- 3. Encapsulation des sous-agents en outils pour le coordinateur ---
@tool
async def flight_specialist(query: str) -> str:
    """Consults the Travel Agent specialist for flight options."""
    res = await travel_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

@tool
async def venue_specialist(query: str) -> str:
    """Consults the Venue Agent specialist to locate wedding venues."""
    res = await venue_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

@tool
async def music_specialist(query: str) -> str:
    """Consults the DJ Agent specialist for music and entertainment."""
    res = await dj_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

@tool
async def writing_specialist(query: str) -> str:
    """Consults the Creative Writing specialist for invitations, speeches, or vows."""
    res = await writer_agent.ainvoke({"messages": [HumanMessage(content=query)]})
    return res["messages"][-1].content

# --- 4. Wedding Coordinator (Superviseur Conversationnel) ---
wedding_coordinator = create_agent(
    model=model,
    tools=[flight_specialist, venue_specialist, music_specialist, writing_specialist],
    system_prompt="""You are the Lead Wedding Planning Coordinator & Conversational Assistant.
Help the user plan their destination wedding step by step. If key details are missing, ask clarifying questions. When ready, consult your specialist tools and synthesize a concise, structured proposal in Markdown."""
)

async def run_wedding_chat(user_message: str, history: list) -> str:
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
    
    res = await wedding_coordinator.ainvoke({"messages": messages})
    return res["messages"][-1].content