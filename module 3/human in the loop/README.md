# LangChain Human-in-the-Loop (HITL) Demo: Approve, Reject, Edit

An experiment showing how to add **human approval** to a LangChain agent before it runs a sensitive action. The agent is **interrupted** before its tools run, and a human can respond in three ways: **approve**, **reject with a reason**, or **edit** the proposed arguments.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Overview

The agent is an automated email assistant with two tools:

| Tool | Risk level | Behavior |
|------|-----------|----------|
| `read_inbox` | Low (read-only) | Resumed **automatically** by the script |
| `send_email_tool` | Sensitive | **Gated**: requires a human decision before it runs |

The agent is built with `interrupt_before=["tools"]` and a `MemorySaver` checkpointer, so execution pauses before every tool call and can be resumed later from the saved state.

The test prompt asks the agent to read the inbox and then send a confirmation email to `client@example.com` quoting **€4,500**.

## The Three Response Modes

| Mode | What the human does | What happens |
|------|---------------------|--------------|
| **Approve** | Accepts the proposed email as is | The agent resumes and the email is sent unchanged. |
| **Reject** | Denies the action with a reason (the quote is wrong) | A `ToolMessage` with the rejection reason is injected into the state, and the agent continues without sending the email. |
| **Edit** | Modifies the proposed arguments (new body with **€4,200**) | The pending tool call is overwritten in the state, a note explains the change, and the agent resumes with the edited email. |

## Project Structure

```
.
├── test_hitl_three_responses.py    # Full HITL experiment (3 modes, 3 threads)
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

   Create a `.env` file in the project folder (or its parent folder, the script checks both):

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

```bash
python test_hitl_three_responses.py
```

The script runs the three modes one after another, each in its own thread (`thread_1`, `thread_2`, `thread_3`), with a 10-second pause between them to avoid rate limits.

### Expected output for each mode

1. The agent reads the inbox automatically.
2. The script prints `Interrupted at gated tool boundary: send_email_tool` along with the proposed arguments.
3. The human decision is applied (approve, reject or edit).
4. The final agent response is printed.

## How It Works

```
User request
     │
     ▼
Agent proposes a tool call
     │
     ▼
interrupt_before=["tools"]  ──► execution paused, state saved by MemorySaver
     │
     ├── read_inbox       ──► resumed automatically
     └── send_email_tool  ──► human decision:
            ├── approve ──► resume with the same arguments
            ├── reject  ──► inject a ToolMessage with the reason
            └── edit    ──► update the tool call arguments, then resume
```

- `agent.astream(...)` runs until the interrupt; `agent.astream(None, config=config)` resumes from the saved state.
- `agent.update_state(...)` is used to inject the rejection message or the edited tool call.
- Each mode uses a separate `thread_id` so the conversations stay isolated.

## Key Takeaways

- Sensitive actions (sending emails, payments, deletions) should require human validation.
- Interrupts plus a checkpointer let an agent **pause, wait for a human, then resume** exactly where it stopped.
- A rejection should give a **reason**, so the agent can adapt instead of retrying the same action.
- Editing the arguments lets the human fix details without restarting the whole conversation.

## Notes

- In this demo the "human" decisions are **scripted** (hardcoded in each mode). In a real application they would come from a UI such as a button or a form.
- The script only treats the tool call at index `0`, so it assumes one tool call at a time.
- Interrupting on the whole `tools` node pauses on every tool, including `read_inbox`, which is why the script resumes that one automatically. Newer LangChain versions also provide built-in human-in-the-loop middleware for `create_agent`, which is a cleaner option for production code.
- `max_tokens=300` is set on the model to stay within Groq's output token quotas.
- On Windows, the script sets `WindowsProactorEventLoopPolicy` to avoid event loop issues.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.