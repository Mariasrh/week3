# LangChain Multi-Agent Supervisor Demo

A small set of experiments showing how to build a **multi-agent system** with LangChain, where a **supervisor agent** delegates tasks to specialized **sub-agents** wrapped as tools. The LLM is served by Groq.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Overview

Both examples use the same pattern, called **"sub-agents as tools"**:

1. Each specialist is a regular agent with its own tools and system prompt.
2. Each specialist is wrapped in an async `@tool` function.
3. A supervisor agent receives these wrapped agents as its tools and decides which one to call.

| File | Supervisor | Sub-agent(s) | What it demonstrates |
|------|------------|--------------|----------------------|
| `test_mini_multi_agent.py` | Task coordinator | Math expert, Spanish translation expert | Delegating **several different tasks** to **several specialists** in one request. |
| `test_split_real_agent.py` | Marketing copywriter | Technical research specialist | A supervisor that **gathers data from a specialist** and uses it to write a product feature sheet. |

## Project Structure

```
.
├── test_mini_multi_agent.py    # Supervisor + math and Spanish sub-agents
├── test_split_real_agent.py    # Copywriter supervisor + research sub-agent
├── .env                        # API keys (not committed)
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
   pip install python-dotenv langchain langchain-groq langchain-core
   ```

3. **Configure your environment variables**

   Create a `.env` file at the root of the project:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

Run each example independently:

```bash
python test_mini_multi_agent.py
python test_split_real_agent.py
```

### Example 1: Math + Translation

The supervisor receives:

> *Calculate 12 times 12, then translate the result 'The result is 144' into Spanish.*

It delegates the calculation to `math_expert_agent` (which uses `multiply_tool`), then the translation to `spanish_expert_agent` (which uses `translate_to_spanish_tool`), and returns the combined answer.

### Example 2: Product Sheet

The supervisor receives:

> *Write a marketing product sheet for the new Laptop Pro.*

It asks `research_specialist` for the technical specifications (via `fetch_tech_specs`), then writes an engaging feature sheet based on them.

## How It Works

```
User request
     │
     ▼
Supervisor agent ──► decides which expert to call
     │
     ├──► Sub-agent A (own tools + system prompt) ──► result
     └──► Sub-agent B (own tools + system prompt) ──► result
     │
     ▼
Final answer
```

- `create_agent` builds each agent (sub-agents and supervisor).
- Each sub-agent is exposed to the supervisor through an async `@tool` that calls `sub_agent.ainvoke(...)` and returns the last message content.
- The tool **docstring** is important: it is what the supervisor reads to decide which expert to call.

## Key Takeaways

- Splitting work between specialized agents keeps each prompt and toolset small and focused.
- A sub-agent wrapped as a tool is just another tool from the supervisor's point of view.
- Clear tool descriptions lead to better delegation.

## Notes

- The tools are **simulated** (`fetch_tech_specs` returns hardcoded specs, `translate_to_spanish_tool` only prefixes the text with `[Spanish]`). They can be replaced with real implementations such as an API or a database lookup.
- On Windows, the scripts set `WindowsProactorEventLoopPolicy` to avoid event loop issues.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.