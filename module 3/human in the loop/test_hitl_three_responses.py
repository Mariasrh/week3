import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent

# Chargement des variables d'environnement depuis le dossier parent si besoin
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
if not os.getenv("GROQ_API_KEY"):
    load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Initialisation du modèle avec max_tokens pour limiter l'utilisation du quota Groq
model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=300)

# --- 1. Définition des Outils ---
@tool
def read_inbox() -> str:
    """Lit les emails reçus (AUTOMATIQUE - Action de lecture sans risque)."""
    return "Email reçu : 'Merci de me confirmer le tarif pour 80 personnes le 15 Juin.'"

@tool
def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Envoie un email (VERROUILLÉ - Action sensible vers un tiers)."""
    return f"✅ EMAIL ENVOYÉ À {recipient} | Sujet: {subject} | Contenu: {body}"

memory = MemorySaver()

# Interruption automatique configurée avant l'exécution des outils
agent = create_agent(
    model=model,
    tools=[read_inbox, send_email_tool],
    checkpointer=memory,
    system_prompt="Tu es un assistant de messagerie. Lis les emails et réponds quand demandé.",
    interrupt_before=["tools"]
)

async def test_response_mode(mode: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n==================================================")
    print(f"🧪 TEST DU MODE : {mode.upper()}")
    print(f"==================================================")
    
    prompt = "Lit mon inbox puis réponds par email pour donner le tarif de 4 500 €."
    
    # Lancement initial : l'agent s'exécute jusqu'à la première interruption
    async for event in agent.astream({"messages": [HumanMessage(content=prompt)]}, config=config):
        pass

    state = memory.get(config)
    last_msg = state['channel_values']['messages'][-1]
    
    # Si le premier outil appelé est read_inbox (automatique), on poursuit jusqu'à l'outil sensible
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls and last_msg.tool_calls[0]['name'] == 'read_inbox':
        print("⚡ Outil 'read_inbox' exécuté automatiquement.")
        async for event in agent.astream(None, config=config):
            pass
        state = memory.get(config)
        last_msg = state['channel_values']['messages'][-1]

    tool_call = last_msg.tool_calls[0]
    print(f"⏸️ Interruption sur l'outil : {tool_call['name']}")
    print(f"📝 Arguments proposés : {tool_call['args']}")

    # --- 2. Application des 3 réponses humaines ---
    if mode == "approve":
        print("\n👉 Action : APPROVE (Approbation sans modification)")
        async for event in agent.astream(None, config=config):
            pass

    elif mode == "reject":
        print("\n👉 Action : REJECT WITH REASON (Rejet avec motif)")
        rejection_msg = ToolMessage(
            content="Action refusée par l'utilisateur : Le tarif de 4500€ est erroné, ne pas envoyer cet email.",
            tool_call_id=tool_call['id']
        )
        # Injection du rejet dans le nœud "tools"
        agent.update_state(config, {"messages": [rejection_msg]}, as_node="tools")
        async for event in agent.astream(None, config=config):
            pass

    elif mode == "edit":
        print("\n👉 Action : EDIT (Édition directe des arguments)")
        edited_args = tool_call['args'].copy()
        
        # 1. Mise à jour des arguments de l'outil avec le montant corrigé
        edited_args['body'] = "Bonjour,\n\nJe vous confirme le tarif ferme de 4 200 € pour 80 personnes le 15 juin.\n\nCordialement"
        last_msg.tool_calls[0]['args'] = edited_args
        
        # 2. Injection d'un message d'instruction utilisateur pour aligner la consigne dans l'historique
        human_note = HumanMessage(
            content="[Instruction Utilisateur HITL] : Le montant du tarif a été ajusté à 4 200 € par l'utilisateur pour cet envoi. Considère ce nouveau montant comme la consigne valide."
        )
        
        agent.update_state(config, {"messages": [last_msg, human_note]})
        async for event in agent.astream(None, config=config):
            pass

    final_state = memory.get(config)
    print(f"\n💬 Réponse finale de l'agent :\n{final_state['channel_values']['messages'][-1].content}")

async def main():
    await test_response_mode("approve", "thread_1")
    
    print("\n⏳ Pause de 10 secondes (Gestion des quotas Groq)...")
    await asyncio.sleep(10)
    
    await test_response_mode("reject", "thread_2")
    
    print("\n⏳ Pause de 10 secondes (Gestion des quotas Groq)...")
    await asyncio.sleep(10)
    
    await test_response_mode("edit", "thread_3")

if __name__ == "__main__":
    asyncio.run(main())