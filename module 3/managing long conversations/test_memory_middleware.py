import sys
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, RemoveMessage, AIMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0)

# --- 1. Outil fournissant la donnée éphémère ---
@tool
def get_secret_temperature(city: str) -> str:
    """Renvoie la température exacte d'une ville."""
    return f"La température exacte enregistrée à {city} est de 42.5°C."

# --- 2. Configuration de l'agent ---
memory = MemorySaver()

agent = create_agent(
    model=model,
    tools=[get_secret_temperature],
    checkpointer=memory,
    system_prompt="Tu es un assistant utile. Utilise tes outils pour répondre aux questions."
)

# --- 3. Scénario de test ---
async def run_middleware_test():
    config = {"configurable": {"thread_id": "session_test_tokens"}}
    
    print("==================================================")
    print("--- 💬 ÉTAPE 1 : Exécution normale avec outil ---")
    print("==================================================")
    prompt1 = "Quelle est la température exacte à Florence ?"
    print(f"Utilisateur : {prompt1}")
    
    res1 = await agent.ainvoke({"messages": [HumanMessage(content=prompt1)]}, config=config)
    print(f"Agent : {res1['messages'][-1].content}")
    
    state_before = memory.get(config)
    msgs_before = state_before['channel_values']['messages']
    print(f"\n📊 Nombre total de messages en mémoire : {len(msgs_before)}")
    
    print("\n==================================================")
    print("--- 🧹 ÉTAPE 2 : Application du Middleware (Purge paire AI+Tool) ---")
    print("==================================================")
    
    # Identification des ToolMessages ET des AIMessages contenant des tool_calls à purger
    msgs_to_remove = []
    for msg in msgs_before:
        if isinstance(msg, ToolMessage):
            msgs_to_remove.append(msg.id)
        elif isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            msgs_to_remove.append(msg.id)
            
    if msgs_to_remove:
        for msg_id in msgs_to_remove:
            agent.update_state(config, {"messages": [RemoveMessage(id=msg_id)]})
        print(f"✅ Supprimé {len(msgs_to_remove)} message(s) d'interaction d'outils (AIMessage + ToolMessage) du State.")

    state_after = memory.get(config)
    msgs_after = state_after['channel_values']['messages']
    print(f"📊 Nombre total de messages en mémoire après purge : {len(msgs_after)}")

    print("\n==================================================")
    print("--- 🧪 ÉTAPE 3 : Test de vérification (Asking the Impossible) ---")
    print("==================================================")
    prompt2 = "Quelle était la valeur exacte de la température renvoyée par l'outil tout à l'heure ?"
    print(f"Utilisateur : {prompt2}")
    
    res2 = await agent.ainvoke({"messages": [HumanMessage(content=prompt2)]}, config=config)
    print(f"\nAgent : {res2['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(run_middleware_test())