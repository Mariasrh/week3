# LangChain Agent: Context & State Demo

A small set of experiments showing how a **LangChain agent** can access **immutable context** (user information) and **modify its own state** (learned preferences), using Groq as the LLM provider.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Overview

The project contains three tests that illustrate the difference between **context** (read-only information passed at invocation time) and **state** (data the agent can update during a conversation).

| Test | File | What it demonstrates |
|------|------|----------------------|
| Test 1 | `test_context_fail.py` | The agent has **no tool** to read the context, so it cannot answer (expected failure). |
| Test 2 | `test_context_success.py` | The agent uses the `get_user_context` tool to read the context and answers correctly. |
| Test 3 | `test_state_learning.py` | The agent **learns a user preference** and writes it into a custom state field via a tool returning a `Command`. |

## Project Structure

```
.
├── context_schema.py          # UserContext model + get_user_context tool
├── test_context_fail.py       # Test 1: agent without the context tool
├── test_context_success.py    # Test 2: agent with the context tool
├── test_state_learning.py     # Test 3: custom state + MemorySaver checkpointer
├── .env                       # API keys (not committed)
└── README.md
```

## Requirements

- Python 3.10+
- A [Groq API key](https://console.groq.com/)

## Installation

1. **Create and activate a virtual environment** (recommended)

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

2. **Install the dependencies**

   ```bash
   pip install python-dotenv pydantic langchain langchain-groq langgraph
   ```

3. **Configure your environment variables**

   Create a `.env` file at the root of the project:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

Run each test independently:

```bash
python test_context_fail.py
python test_context_success.py
python test_state_learning.py
```

### Expected behavior

- **Test 1**: the agent cannot know the user's role or language because it has no way to read the context.
- **Test 2**: the agent calls `get_user_context` and replies with the user's role (`customer`) and preferred language (`Spanish`).
- **Test 3**: the agent calls `save_user_preference`, and the script prints the updated `learned_preference` field from the state.

## How It Works

### Context (`context_schema.py`)

- `UserContext` is a Pydantic model holding `user_id`, `role` and `preferred_language`.
- The context is passed through `config["configurable"]["context"]` when invoking the agent.
- `get_user_context` is a tool that reads this context from the `RunnableConfig`, so the LLM can access it only through a tool call.

### State (`test_state_learning.py`)

- `CustomAgentState` extends the default state with a `learned_preference` field, and uses the `add_messages` reducer for the `messages` channel.
- `save_user_preference` returns a LangGraph `Command` that updates `learned_preference` **and** appends the required `ToolMessage`.
- `MemorySaver` is used as a checkpointer, which allows reading the state afterwards with `agent.aget_state(config)`.

## Key Takeaways

- **Context** is read-only information provided at invocation time; the agent needs a tool to see it.
- **State** is mutable and can be updated by tools through `Command(update=...)`.
- A tool that updates the state must also return a `ToolMessage` linked to its `tool_call_id`.

## Notes

- On Windows, the scripts set `WindowsProactorEventLoopPolicy` to avoid event loop issues.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Pydantic](https://docs.pydantic.dev/)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.