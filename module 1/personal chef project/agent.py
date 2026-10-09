import os
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

load_dotenv()

search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

system_prompt = (
    "You are a creative and pragmatic chef. "
    "The user will give you a list of ingredients they have left in their kitchen. "
    "Use the web search tool to find recipes suitable for these ingredients. "
    "Suggest concrete ideas and answer follow-up questions to help the user."
)

model = ChatGroq(model="qwen/qwen3.8-27b", temperature=0.7)

agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=system_prompt
)

if __name__ == "__main__":
    checkpointer = MemorySaver()
    agent_with_memory = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt,
        checkpointer=checkpointer
    )

    config = {"configurable": {"thread_id": "session_interactive_1"}}

    print("==================================================")
    print("         Assistant Chef (LangGraph)               ")
    print("     Type 'quit' or 'exit' to close the chat      ")
    print("==================================================\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Chef: Goodbye and bon appétit!")
            break

        if not user_input.strip():
            continue

        response = agent_with_memory.invoke(
            {"messages": [("user", user_input)]},
            config=config
        )

        bot_response = response["messages"][-1].content
        print(f"\nChef: {bot_response}\n")