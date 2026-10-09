import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

# --- Chargement des variables d'environnement ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
if not os.getenv("GROQ_API_KEY"):
    load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- Modèles actifs issus de votre API Groq ---
MODEL_CHEAP_NAME = "openai/gpt-oss-20b"   # Petit modèle économique
MODEL_CAPABLE_NAME = "qwen/qwen3.8-27b"    # Grand modèle pour requêtes complexes

model_cheap = ChatGroq(model=MODEL_CHEAP_NAME, temperature=0, max_tokens=300)
model_capable = ChatGroq(model=MODEL_CAPABLE_NAME, temperature=0, max_tokens=300)

# --- 1. Définition des Outils ---
@tool
def web_search(query: str) -> str:
    """Outil public : recherche sur le web."""
    return f"Résultat public pour '{query}' : Information accessible à tous."

@tool
def internal_db(query: str) -> str:
    """Outil confidentiel : réservé au personnel interne."""
    return f"Résultat confidentiel pour '{query}' : Données RH/Finances secrètes."

# --- 2. Middleware Wrap-Style (Agent Dynamique) ---
memory = MemorySaver()

async def run_dynamic_agent(input_state: dict, config: dict):
    """
    Intercepte l'appel pour modifier en temps réel :
    1. Le Prompt Système (adaptation à la langue)
    2. Les Outils (filtrage selon le rôle / RBAC)
    3. Le Modèle (basculement selon la taille de la conversation)
    """
    configurable = config.get("configurable", {})
    user_role = configurable.get("user_role", "external")
    user_lang = configurable.get("user_lang", "fr")
    messages = input_state.get("messages", [])
    
    # TÂCHE 1 : Prompt Dynamique
    if user_lang == "es":
        system_prompt = "Eres un asistente servicial. Responde siempre en español con tono profesional."
    elif user_lang == "en":
        system_prompt = "You are a helpful assistant. Always answer in English with a professional tone."
    else:
        system_prompt = "Tu es un assistant utile. Réponds toujours en français de manière professionnelle."

    # TÂCHE 2 : Masquage d'outils (RBAC)
    if user_role == "internal":
        tools = [web_search, internal_db]
    else:
        # Masquage complet de l'outil sensible pour l'utilisateur externe
        tools = [web_search]

    # TÂCHE 3 : Basculement dynamique de modèle
    msg_count = len(messages)
    if msg_count > 10:
        selected_model = model_capable
        model_label = f"{MODEL_CAPABLE_NAME} (Grand Modèle)"
    else:
        selected_model = model_cheap
        model_label = f"{MODEL_CHEAP_NAME} (Petit Modèle)"

    print(f"  🔧 [WRAP MIDDLEWARE] Msgs: {msg_count} | Rôle: '{user_role}' | Langue: '{user_lang}' | Modèle: {model_label}")

    # Reconstitution dynamique de l'agent pour cette requête
    agent = create_agent(
        model=selected_model,
        tools=tools,
        checkpointer=memory,
        system_prompt=system_prompt
    )
    
    return await agent.ainvoke(input_state, config=config)

# --- 3. Scénarios de Test ---
async def run_tests():
    print("==================================================")
    print("🎯 TEST 1 : Prompt Dynamique (Changement de langue)")
    print("==================================================")
    
    config_es = {"configurable": {"thread_id": "thread_lang", "user_lang": "es", "user_role": "external"}}
    res_es = await run_dynamic_agent({"messages": [HumanMessage(content="Bonjour, comment vas-tu ?")]}, config=config_es)
    print(f"Agent (Espagnol) : {res_es['messages'][-1].content}\n")

    print("==================================================")
    print("🎯 TEST 2 : Masquage d'outil selon le rôle (RBAC)")
    print("==================================================")
    
    prompt_db = "Cherche les données RH confidentielles dans la base interne."
    
    # Externe (Ne voit pas internal_db)
    config_ext = {"configurable": {"thread_id": "thread_ext", "user_lang": "fr", "user_role": "external"}}
    print("👉 Tentative par un utilisateur EXTERNE :")
    res_ext = await run_dynamic_agent({"messages": [HumanMessage(content=prompt_db)]}, config=config_ext)
    print(f"Agent (Externe) : {res_ext['messages'][-1].content}\n")

    # Interne (A accès à internal_db)
    config_int = {"configurable": {"thread_id": "thread_int", "user_lang": "fr", "user_role": "internal"}}
    print("👉 Tentative par un utilisateur INTERNE :")
    res_int = await run_dynamic_agent({"messages": [HumanMessage(content=prompt_db)]}, config=config_int)
    print(f"Agent (Interne) : {res_int['messages'][-1].content}\n")

    print("==================================================")
    print("🎯 TEST 3 : Basculement de modèle (> 10 messages)")
    print("==================================================")
    
    config_switch = {"configurable": {"thread_id": "thread_switch", "user_lang": "fr", "user_role": "internal"}}
    
    # Simulation d'un historique long (> 10 messages)
    dummy_history = []
    for i in range(11):
        dummy_history.append(HumanMessage(content=f"Message {i+1}"))
        dummy_history.append(AIMessage(content=f"Réponse {i+1}"))
    
    dummy_history.append(HumanMessage(content="Fais un résumé rapide de nos échanges."))
    
    res_switch = await run_dynamic_agent({"messages": dummy_history}, config=config_switch)
    print(f"Agent (Grand Modèle) : {res_switch['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(run_tests())