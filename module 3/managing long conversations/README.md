# LangChain Agent Memory & Before-Model Middleware Demo

An experiment showing how to **filter an agent's conversation history before it reaches the LLM**, using a custom model wrapper that acts as a *before-model middleware*. The agent keeps its full memory in a checkpointer, but the model no longer sees the tool results and tool-related messages.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Overview

The script runs a conversation with an agent that has memory (`MemorySaver`) and one tool, `get_secret_temperature`, which returns an "ephemeral" piece of data (`42.5°C`). It then turns on a filter and checks whether the model can still recall that data.

| Step | Description |
|------|-------------|
| **Task 1** | Run a short conversation (3 questions, including one that triggers the tool) and print the number of messages stored in memory, plus token usage per run. |
| **Task 2** | Activate the middleware filter (`purge_active = True`). |
| **Task 3** | Ask the agent to recall the temperature returned by the tool earlier, and compare the behavior and token usage. |

## Project Structure

```
.
├── test_memory_middleware.py    # Full experiment (agent, middleware wrapper, test flow)
├── .env                         # API keys (not committed)
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
   pip install python-dotenv langchain langchain-core langchain-groq langgraph
   ```

3. **Configure your environment variables**

   Create a `.env` file at the root of the project:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

```bash
python test_memory_middleware.py
```

### Expected behavior

- During Task 1, the agent calls `get_secret_temperature` and answers with `42.5°C`.
- During Task 3, the middleware removes tool messages and tool-call messages from the history before each model call, so the agent should **no longer be able to recall the exact value** returned by the tool.
- The prompt token count is printed at each step so you can compare how much context is sent to the model.

## How It Works

```
Checkpointer (MemorySaver)  ──► full history kept intact
            │
            ▼
   FilteredChatGroq.ainvoke()   ◄── before-model middleware
            │   if purge_active:
            │     - drop ToolMessage
            │     - drop AIMessage with tool calls
            │     - drop AIMessage mentioning "42.5"
            ▼
         ChatGroq (LLM)
```

- `FilteredChatGroq` is a thin wrapper around `ChatGroq`. It forwards `bind_tools` (so `create_agent` can attach tools) and intercepts `ainvoke` to filter the messages.
- The global flag `purge_active` turns the filtering on and off during the run.
- Filtering only affects what is **sent to the model**: the messages stay stored in the checkpointer.

## Key Takeaways

- Agent memory (the stored history) and the model's context (what it actually sees) can be controlled separately.
- Removing old tool outputs from the context reduces token usage and can prevent sensitive or ephemeral data from being reused.
- Filtering must keep the message history valid for the provider: dropping a tool-call message without its tool result (or the reverse) can cause API errors, which is why both are removed together here.

## Notes

- The filter in this demo is intentionally simple and hardcoded (it looks for the string `"42.5"`). It is meant for learning, not production use.
- The wrapper filters messages **in place** on the input it receives, which is fine for a demo but worth reviewing in a real project.
- LangChain also offers built-in middleware mechanisms for `create_agent`, which are a cleaner option for production code.
- On Windows, the script sets `WindowsProactorEventLoopPolicy` to avoid event loop issues.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.