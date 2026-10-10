# LangChain Short-Term Memory Demo: Stateless Agent vs Checkpointer & Threads

A Jupyter notebook showing how **short-term memory** works in a LangChain / LangGraph agent. It compares an agent that **forgets everything** between calls with an agent that remembers thanks to a **checkpointer**, and shows how **thread IDs** keep conversations separate. The LLM is served by Groq.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## What the Notebook Covers

| Task | Agent | Scenario | Result |
|------|-------|----------|--------|
| **Task 1** | Stateless (no checkpointer) | Tell the agent "My favorite color is green", then ask "What is my favorite color?" | The agent **forgets**: each call starts from scratch. |
| **Task 2** | With `MemorySaver`, thread `session_alpha` | Same two messages in the same thread | The agent **remembers** and answers "green". The message history is printed. |
| **Task 3** | Same agent, new thread `session_beta` | Ask "What is my favorite color?" | The agent **does not know**: a new thread means a new, empty conversation. |

## Project Structure

```
.
├── short memory.ipynb    # The notebook
├── .env                  # API keys (not committed)
└── README.md
```

## Requirements

- Python 3.10+
- Jupyter (JupyterLab, Jupyter Notebook or VS Code with the Jupyter extension)
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
   pip install python-dotenv langchain langchain-core langchain-groq langgraph jupyter
   ```

3. **Configure your environment variables**

   Create a `.env` file next to the notebook:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

```bash
jupyter notebook "short memory.ipynb"
```

Run the cells from top to bottom and compare the three outputs.

## How It Works

```
Task 1: no checkpointer                Task 2: with MemorySaver
┌──────────────┐                       ┌──────────────┐
│ invoke #1    │  state discarded      │ invoke #1    │──┐ saved under
└──────────────┘                       └──────────────┘  │ thread_id
┌──────────────┐                       ┌──────────────┐  │ "session_alpha"
│ invoke #2    │  knows nothing        │ invoke #2    │◄─┘ history reloaded
└──────────────┘                       └──────────────┘

Task 3: same agent, thread_id "session_beta" ──► empty history ──► knows nothing
```

- Without a checkpointer, each `invoke` only sees the messages passed in that call.
- With `MemorySaver`, the state is saved after every step and reloaded from the `thread_id` given in `config["configurable"]`.
- Passing the same `thread_id` continues the conversation. A different `thread_id` starts a separate one.
- The notebook prints the stored message list (human and AI messages) to show exactly what the agent remembers.

## Key Takeaways

- LLMs are **stateless by default**: memory must be provided by the application.
- A **checkpointer** gives an agent short-term memory within a conversation.
- The **`thread_id`** identifies a conversation: it isolates users and sessions from each other.
- Short-term memory is not long-term memory: information from one thread is not shared with another.

## Notes

- `MemorySaver` keeps data **in RAM only**. It is lost when the kernel restarts. For persistence across restarts, use a database-backed checkpointer (for example SQLite or Postgres).
- The model runs at `temperature=0.0`, so the answers are mostly consistent across runs.
- The full history grows with every message and is sent to the model each time, so long conversations increase token usage. Trimming or summarizing messages can help.
- The model name (`qwen/qwen3.8-27b`) is set in the `ChatGroq` call. If it stops working, check the models currently available on your Groq account and update it.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/) and [Jupyter](https://jupyter.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph) (checkpointers)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.
