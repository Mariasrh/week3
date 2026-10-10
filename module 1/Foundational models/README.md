# LangChain Agent Basics: Models, Response Metadata & System Prompts

A Jupyter notebook covering the fundamentals of working with a LLM and a simple agent in LangChain: how to call a model, how to read the full response object (including metadata and token usage), and how a **system prompt with few-shot examples** shapes an agent's behavior. The LLM is served by Groq.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## What the Notebook Covers

| Section | Topic | What it shows |
|---------|-------|---------------|
| **1** | Setup | Loading the environment variables (`GROQ_API_KEY`) with `python-dotenv`. |
| **2** | Model & response object | Initializing `ChatGroq`, invoking it, and inspecting the full `AIMessage`: content, `response_metadata`, token usage, model name and finish reason. |
| **3** | System prompt + few-shot examples | Creating an agent with `create_agent` and a system prompt that forces a **one-word analogy** answer. |
| **4** | Changing the behavior | The same agent pattern with a different system prompt that forces **exactly two emojis** and no text. |

### Section 2: Reading the response object

After `llm.invoke(...)`, the notebook prints:

- the full response object,
- `response_metadata["token_usage"]` (prompt, completion and total tokens, plus timing),
- the model name and the finish reason,
- the text only, with `response.content`.

### Sections 3 and 4: Prompt-driven behavior

With no tools (`tools=[]`), the agent's behavior is controlled only by its system prompt. Few-shot examples teach the format of the expected answer:

| Prompt style | Question | Output |
|--------------|----------|--------|
| One-word analogy translator | *What is Kubernetes?* | A single word (for example `Captain`) |
| Two-emoji responder | *What is Cloud Computing?* | Two emojis (for example `☁️💻`) |

Note that the model runs with `temperature=0.7`, so the one-word answer can differ between runs (the notebook shows both `Shepherd` and `Captain` for the same question).

## Project Structure

```
.
├── 1_agent_basics.ipynb    # The notebook
├── .env                    # API keys (not committed)
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

Start Jupyter and open the notebook:

```bash
jupyter notebook 1_agent_basics.ipynb
```

Then run the cells from top to bottom.

## Key Takeaways

- A model response is more than text: `response_metadata` and `usage_metadata` give you token counts, timing, the model name and the finish reason, which are useful for monitoring cost and latency.
- The **system prompt** is the main way to control tone, format and behavior of an agent.
- **Few-shot examples** in the prompt are a simple and effective way to enforce a strict output format.
- Settings such as `temperature` and `max_tokens` control how varied and how long the answers are. A higher temperature gives more variation between runs.

## Notes

- The notebook title mentions `create_react_agent`, but the agent cells use `create_agent` from `langchain.agents`. The `create_react_agent` import from `langgraph.prebuilt` is not used and can be removed.
- The introduction mentions comparing low and high temperature. The notebook only runs the model at `temperature=0.7`, so a low-temperature run (for example `temperature=0`) could be added to complete the comparison.
- The model name (`qwen/qwen3.8-27b`) is set in the `ChatGroq` call. If it stops working, check the models currently available on your Groq account and update it.
- The cells in sections 3 and 4 repeat the same pattern with different prompts, which makes the effect of the system prompt easy to compare.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/) and [Jupyter](https://jupyter.org/)
- [LangChain](https://www.langchain.com/)
- [LangGraph](https://www.langchain.com/langgraph)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.
