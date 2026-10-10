# LangChain Dynamic Agent Demo: Prompt, Tools & Model Switching

An experiment showing how to **configure a LangChain agent dynamically at runtime** based on who is asking and how long the conversation is. A wrapper function inspects the request and builds the agent with the right **system prompt**, **tools** and **model** each time.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Overview

The script runs three tasks, each demonstrating one kind of dynamic behavior:

| Task | Behavior | Decision based on |
|------|----------|-------------------|
| **Task 1** | **Dynamic system prompt** | User language (`es`, `en`, `fr`) and role |
| **Task 2** | **Tool hiding by role (RBAC)** | User role (`internal` or `external`) |
| **Task 3** | **Dynamic model switching** | Number of messages in the conversation |

### Task 1: Dynamic Prompt

The system prompt changes with the user's language (Spanish, English or French by default). Internal users get a dedicated prompt telling the agent to use the internal database tool right away.

### Task 2: Tool Hiding by Role (RBAC)

| Role | Available tools | Model |
|------|-----------------|-------|
| `external` | `web_search` | Cheap model |
| `internal` | `web_search`, `internal_db` | Capable model |

An external user asking for internal records cannot trigger `internal_db`, because the tool is **never given** to the agent.

### Task 3: Model Switching

For external users, the model depends on the message count: the **cheap model** (`openai/gpt-oss-20b`) is used up to 10 messages, then the script switches to the **capable model** (`qwen/qwen3.8-27b`). Token usage is printed so the two runs can be compared.

## Project Structure

```
.
├── test_dynamic_middleware.py    # Full experiment (dynamic agent + 3 tasks)
├── .env                          # API keys (not committed)
└── README.md
```

## Requirements

- Python 3.10+
- A [Groq API key](https://console.groq.com/) (starting with `gsk_`)

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

   Create a `.env` file in the project folder (the script also checks the parent and grandparent folders):

   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

   Or set the variable directly in PowerShell:

   ```powershell
   $env:GROQ_API_KEY='gsk_your_key_here'
   ```

## Usage

```bash
python test_dynamic_middleware.py
```

The script exits with an error message if `GROQ_API_KEY` is missing or does not start with `gsk_`.

### Expected output

- A `[WRAP MIDDLEWARE]` line before each run showing the message count, role, language and the model that was selected.
- **Task 1:** the agent answers in Spanish, even though the question is in French.
- **Task 2:** the external user does not get access to internal records, while the internal user triggers `internal_db`.
- **Task 3:** two runs of the same question with token counts, one on each model.

## How It Works

```
Request (messages + config: user_role, user_lang)
        │
        ▼
run_dynamic_agent()   ◄── wrap-style middleware
        │   1. choose the system prompt (language / role)
        │   2. choose the tools (role)
        │   3. choose the model (role / message count)
        ▼
create_agent(model, tools, system_prompt)
        │
        ▼
agent.ainvoke(...)
```

- `user_role` and `user_lang` are passed through `config["configurable"]`.
- A new agent is built on each call with the selected prompt, tools and model, and all of them share the same `MemorySaver` checkpointer.
- `print_token_stats` reads the token usage from the response metadata.

## Key Takeaways

- A single entry point can serve different users with different prompts, tools and models.
- **Hiding a tool** is safer than only telling the model not to use it: an agent cannot call a tool it was never given.
- Routing short conversations to a cheaper model and longer ones to a more capable model can reduce cost.

## Notes

- This demo rebuilds the agent on every call, which is simple and clear for learning. In a real project, LangChain's built-in middleware for `create_agent` (dynamic prompt, model selection, tool filtering) is a cleaner option.
- The language rule has priority over the internal role: an internal user with `user_lang="es"` gets the Spanish prompt, not the internal one.
- Role-based access control here relies on a value passed in the config. In production it should come from a trusted source such as authentication, not from client input.
- `max_tokens=300` is set on the models to stay within Groq's output token quotas.
- On Windows, the script sets `WindowsProactorEventLoopPolicy` to avoid event loop issues.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.