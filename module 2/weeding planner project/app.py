import sys
import asyncio
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from wedding_team import run_wedding_chat
from trip_team import run_trip_chat

async def wedding_chat_interface(message, history):
    try:
        await asyncio.sleep(2)
        return await run_wedding_chat(message, history)
    except Exception as e:
        return f"⚠️ Execution Error: {str(e)}"

async def plan_trip_chat_interface(message, history):
    try:
        await asyncio.sleep(2)
        return await run_trip_chat(message, history)
    except Exception as e:
        return f"⚠️ Execution Error: {str(e)}"

with gr.Blocks(title="Multi-Agent Chat Studio") as demo:
    gr.Markdown(
        """
        # 🤖 Multi-Agent Conversational Planning Studio
        ### Chat with the Coordinator. Specialists (Flights, Venues, Music, Writing) will be consulted as needed.
        """
    )
    
    with gr.Tabs():
        #  WEDDING PLANNER CHAT 
        with gr.TabItem("💒 Wedding Planner Assistant"):
            gr.ChatInterface(
                fn=wedding_chat_interface,
                examples=[
                    "I want to plan a wedding in Florence, Italy for 80 guests departing from Paris in June 2027.",
                    "Can you find flight options from Paris to Florence and recommend a venue for 80 guests?",
                    "Draft an invitation email for our guests and suggest a DJ package with Jazz & Soul music."
                ]
            )
            
        #  PERSONAL TRIP PLANNER CHAT 
        with gr.TabItem("✈️ Personal Trip Assistant"):
            gr.ChatInterface(
                fn=plan_trip_chat_interface,
                examples=[
                    "Plan a 5-day cultural trip to Kyoto departing from London with a mid-range budget.",
                    "What are the best hotels and culinary activities in Kyoto?"
                ]
            )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())