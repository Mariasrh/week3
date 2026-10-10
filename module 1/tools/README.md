# LangChain Agent Tools: Tool Calls, Descriptions & Search

A Jupyter notebook (Lesson 2) about **tools** in LangChain agents: how an agent decides to call a tool, why the **tool description** matters, and how a **search tool** fixes outdated knowledge. The LLM is served by Groq.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## What the Notebook Covers

| Task | Topic | What it shows |
|------|-------|---------------|
| **Task 1** | Custom tool & message trace | Creates a shipping-cost tool and prints the full message trace of the agent loop. |
| **Task 2** | Bad vs. good tool descriptions | Compares vague tools with clearly described ones on two examples (price calculation and discount). |
| **Task 3** | Knowledge cutoff & search tool | Asks about a recent event with and without a web search tool. |

### Task 1: Tools and the Agent Execution Loop

A custom tool, `calculate_shipping_cost(weight_kg, distance_km)`, is given to an agent. The notebook prints every message to show the loop:

```
HumanMessage ─► AIMessage (empty content + tool_calls) ─► ToolMessage ─► AIMessage (final answer)
```

The key observation is that the first `AIMessage` has **empty content**: the model does not answer directly, it only requests a tool call.

### Task 2: Bad vs. Good Tool Descriptions

The same task is given to two agents, one with a poorly described tool and one with a clear one:

| Example | Bad tool | Good tool |
|---------|----------|-----------|
| Total price | `do_thing` ("Stuff.") | `calculate_total_price` (multiplies quantity by unit price) |
| Discount | `process` ("Processes x and y.") | `calculate_discounted_price` (applies a percentage discount to the original price) |

A tool's **name, parameter names and docstring** are what the model reads to decide when and how to use it. Vague ones make the model guess.

### Task 3: Knowledge Cutoff and Search Tool

The question is *"Who won the FIFA World Cup 2026 final match and what was the score?"*

- **Without a tool**, the model has no access to recent events, so it can refuse or invent an answer (hallucination).
- **With a Tavily search tool** (`max_results=3`) and a system prompt requiring it to verify results, the agent searches the web and answers from live data.

## Project Structure

```
.
├── 2_agent_tools.ipynb    # The notebook
├── .env                   # API keys (not committed)
└── README.md
```

## Requirements

- Python 3.10+
- Jupyter (JupyterLab, Jupyter Notebook or VS Code with the Jupyter extension)
- A [Groq API key](https://console.groq.com/)
- A [Tavily API key](https://tavily.com/) (for Task 3)

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
   pip install python-dotenv langchain langchain-core langchain-groq langchain-community tavily-python jupyter
   ```

3. **Configure your environment variables**

   Create a `.env` file next to the notebook:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

```bash
jupyter notebook 2_agent_tools.ipynb
```

Run the cells from top to bottom. Task 3 stops with an error message if `TAVILY_API_KEY` is missing.

## Key Takeaways

- An agent calls a tool by returning an `AIMessage` with `tool_calls`, then receives the result in a `ToolMessage` before writing the final answer.
- **Good tool descriptions are essential**: a clear name, clear parameters and a clear docstring make tool selection reliable.
- LLMs have a **knowledge cutoff**: for recent facts they need a search tool, otherwise they may hallucinate.
- A system prompt can require the agent to use a tool instead of answering from memory.

## Notes

- The model name (`qwen/qwen3.8-27b`) is set in the `ChatGroq` call. If it stops working, check the models currently available on your Groq account and update it.
- `TavilySearchResults` from `langchain_community` may show deprecation warnings in recent versions. The newer `langchain-tavily` package provides an updated Tavily tool.
- The notebook uses `temperature=0.0` so tool selection and answers stay as consistent as possible.
- Search results depend on live web data, so the answer to Task 3 can vary over time.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/) and [Jupyter](https://jupyter.org/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://groq.com/)
- [Tavily](https://tavily.com/) (web search)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.
