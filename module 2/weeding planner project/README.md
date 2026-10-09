# Multi-Agent Conversational Planning Studio

A **Gradio** web app where users chat with **multi-agent teams** built with LangChain and powered by Groq. Each team has a **coordinator (supervisor) agent** that talks to the user and consults **specialist sub-agents** only when needed.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## Features

The app has two tabs, each with its own chat interface:

### 💒 Wedding Planner Assistant (`wedding_team.py`)

A **Wedding Coordinator** that asks clarifying questions and then consults:

| Specialist | Tool | Role |
|------------|------|------|
| Travel agent | `search_flights_tool` | Flight options to the destination |
| Venue scout | `search_venues_tool` | Wedding venues and villas |
| DJ / musical director | `search_music_tool` | Playlists and DJ packages |
| Creative writer | `generate_writing_tool` | Invitations, vows and speeches |

### ✈️ Personal Trip Assistant (`trip_team.py`)

A **Travel Advisor** that builds a concise itinerary by consulting:

| Specialist | Tool | Role |
|------------|------|------|
| Flight expert | `search_trip_flights` | Flight routes |
| Accommodation specialist | `search_hotels` | Hotels by budget level |
| Tour guide | `search_activities` | Sights, culture and food |

## Project Structure

```
.
├── app.py             # Gradio interface (two chat tabs)
├── wedding_team.py    # Wedding coordinator + 4 specialist sub-agents
├── trip_team.py       # Trip supervisor + 3 specialist sub-agents
├── c.py               # Utility script: lists the models available on Groq
├── .env               # API keys (not committed)
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
   pip install gradio python-dotenv langchain langchain-core langchain-groq groq
   ```

3. **Configure your environment variables**

   Create a `.env` file at the root of the project:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

Start the app:

```bash
python app.py
```

Then open the local URL shown in the terminal (usually `http://127.0.0.1:7860`).

### Example prompts

**Wedding tab**
- *I want to plan a wedding in Florence, Italy for 80 guests departing from Paris in June 2027.*
- *Draft an invitation email for our guests and suggest a DJ package with Jazz & Soul music.*

**Trip tab**
- *Plan a 5-day cultural trip to Kyoto departing from London with a mid-range budget.*
- *What are the best hotels and culinary activities in Kyoto?*

### Check the available Groq models

If a model name stops working, list the models currently available on your account:

```bash
python c.py
```

Then update the `model=` value in `wedding_team.py` and `trip_team.py`.

## How It Works

```
User message (Gradio chat)
        │
        ▼
Coordinator / Supervisor agent ──► asks questions or decides who to consult
        │
        ├──► Specialist sub-agent A (own tool + system prompt)
        ├──► Specialist sub-agent B (own tool + system prompt)
        └──► ...
        │
        ▼
Synthesized answer shown in the chat
```

- Each specialist is created with `create_agent` and has its own tool and system prompt.
- Each specialist is wrapped in an async `@tool` so the coordinator can call it like any other tool.
- `run_wedding_chat` and `run_trip_chat` convert the Gradio history (dict or tuple format) into LangChain messages and invoke the coordinator.
- `app.py` adds a 2-second delay before each call and catches exceptions to show a friendly error in the chat.

## Notes

- All tools are **simulated**: they return hardcoded flights, venues, hotels and activities. They can be replaced with real API calls.
- `max_tokens=350` is set on the model to stay within Groq's output token quotas, so answers are intentionally concise.
- The short delay in `app.py` helps avoid rate-limit errors on the free tier.
- Only the user's previous messages are sent as history, not the assistant's replies.
- On Windows, the scripts set `WindowsProactorEventLoopPolicy` to avoid event loop issues.
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/)
- [LangChain](https://www.langchain.com/)
- [Gradio](https://www.gradio.app/)
- [Groq](https://groq.com/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.