# Secure Email Agent: Authentication Gate + Human-in-the-Loop

An interactive command-line chat with a LangChain agent that **must authenticate the user first** before it can access any email tool. Once authenticated, the agent can read the inbox, and every **email sending** requires explicit **human approval**.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Overview

The agent changes its behavior depending on the authentication status found in the conversation history:

| State | System prompt | Available tools | Interrupts |
|-------|---------------|-----------------|------------|
| **Not authenticated** | "Strict security doorman" | `authenticate` only | None |
| **Authenticated** | "Authorized email assistant" | `read_inbox`, `send_email` | Before every tool call |

### Tools

| Tool | Behavior |
|------|----------|
| `authenticate` | Checks the email and password. Returns `SUCCESS:` or `FAILURE:`. |
| `read_inbox` | Reads incoming emails. Runs **automatically**. |
| `send_email` | Sends an email. Requires **human approval** (yes/no) in the terminal. |

## Project Structure

```
.
├── authenticated_email_agent.py    # Interactive secure email agent
├── .env                            # API keys (not committed)
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

   Create a `.env` file in the project folder (the script also checks the parent and grandparent folders):

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

> ⚠️ **Security:** Never write your API key directly in the source code, and never commit your `.env` file. Add it to `.gitignore`.

## Usage

```bash
python authenticated_email_agent.py
```

Type `exit` or `quit` to leave the chat.

### Example session

1. Ask something like *"Read my inbox"*: the agent refuses and asks you to authenticate.
2. Provide the demo credentials defined in `SECRET_CONTEXT` inside the script.
3. Ask again *"Read my inbox"*: the agent now reads it automatically.
4. Ask *"Reply to the client confirming the discount"*: the terminal shows the proposed email (recipient, subject, body) and asks `Approve sending this email? (yes/no)`.

## How It Works

```
User message
     │
     ▼
Is there a ToolMessage containing "SUCCESS:" in the history?
     │
     ├── No  ──► agent with [authenticate] only
     └── Yes ──► agent with [read_inbox, send_email] + interrupt_before=["tools"]
                        │
                        ├── read_inbox  ──► resumed automatically
                        └── send_email  ──► human approval (yes / no)
```

- `run_authenticated_agent` checks the message history stored in the `MemorySaver` checkpointer and **rebuilds the agent** with the right prompt, tools and interrupt settings.
- Email tools are **never given** to the agent before authentication, so it cannot call them even if asked.
- After each user message, a loop resolves pending tool calls: safe tools run automatically, while `send_email` waits for the user's decision.
- Rejecting the approval cancels the sending and returns control to the user.

## Key Takeaways

- Hiding tools until the user is authenticated is safer than only instructing the model not to use them.
- Sensitive actions (like sending an email) should require explicit human validation.
- The authentication state can be derived from the conversation history stored in the checkpointer.

## Notes

- This is a **learning demo**. Credentials are hardcoded in `SECRET_CONTEXT` and the tools are simulated (the inbox is fixed and no real email is sent).
- In a real application, authentication should use a proper identity system, passwords should never be stored in plain text, and credentials should not pass through the LLM.
- When approval is rejected, the pending tool call stays in the saved history. A cleaner approach would be to inject a `ToolMessage` explaining the rejection.
- Only the first tool call (index `0`) is handled at each step.
- `max_tokens=400` is set on the model to stay within Groq's output token quotas.
- On Windows, the script sets `WindowsProactorEventLoopPolicy` to avoid event loop issues.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.