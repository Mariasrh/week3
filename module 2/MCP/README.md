# MCP Multi-Server Agent with LangChain & Groq

A small demo project showing how to connect a **LangChain agent** to multiple **MCP (Model Context Protocol) servers** at the same time: one custom local server and one public server.

> 🎓 This project was built during my training with **ThirdUni**.

---

## Overview

The agent uses an LLM served by **Groq** and discovers its tools dynamically from two MCP servers over the `stdio` transport:

| Server | Type | Tools |
|--------|------|-------|
| `small_server` | Local (custom, built with `FastMCP`) | `add_numbers` – adds two numbers |
| `time_server` | Public (`mcp-server-time`) | Time and timezone tools (configured for `Europe/Paris`) |

The agent then decides on its own which tool to call depending on the user's question.

## Project Structure

```
.
├── main.py             # Runs the LangChain agent with both MCP servers
├── my_small_server.py  # Custom local MCP server (addition tool)
├── test_mcp.py         # Checks that each MCP server starts and exposes its tools
├── .env                # API keys (not committed)
└── README.md
```

## Requirements

- Python 3.10+
- A [Groq API key](https://console.groq.com/)

## Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Create and activate a virtual environment** (recommended)

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install the dependencies**

   ```bash
   pip install python-dotenv langchain langchain-groq langchain-mcp-adapters mcp mcp-server-time
   ```

4. **Configure your environment variables**

   Create a `.env` file at the root of the project:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

### 1. Test the MCP servers

Before running the agent, check that both servers start correctly and list their tools:

```bash
python test_mcp.py
```

### 2. Run the agent

```bash
python main.py
```

The script runs two tests:

1. **Local tool only** – asks the agent to add `1234` and `5678` using the custom `add_numbers` tool.
2. **Public tool only** – asks the agent for the current time in Paris using the `mcp-server-time` server.

## How It Works

1. `MultiServerMCPClient` launches each MCP server as a subprocess using `stdio`.
2. `client.get_tools()` collects the tools exposed by all servers.
3. `ChatGroq` provides the LLM.
4. `create_agent` builds an agent that can call those tools.
5. `agent.ainvoke(...)` sends a question and returns the final answer.

## Adding Your Own Tool

Add a new function to `my_small_server.py`:

```python
@mcp.tool()
def multiply_numbers(a: float, b: float) -> str:
    """Multiplies two numbers and returns the result."""
    return f"The result of {a} x {b} is {a * b}"
```

Restart `main.py` and the agent will discover it automatically.

## Notes

- On Windows, the scripts set `WindowsProactorEventLoopPolicy` so that subprocess-based `stdio` transport works correctly.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.