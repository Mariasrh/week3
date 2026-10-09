# 👨‍🍳 AI Chef Assistant

A simple AI assistant that suggests recipes based on the ingredients you have left in your kitchen.

> 🎓 This project was built during my training with **THIRDUNI**.

## ✨ Features

- Suggests recipes from a list of ingredients
- Searches the web (DuckDuckGo) for recipe ideas
- Remembers the conversation, so you can ask follow-up questions
- Two interfaces: a Streamlit web app and a terminal chat

## 🧰 Tech Stack

- Python
- LangGraph (ReAct agent)
- Groq (LLM) via `langchain-groq`
- DuckDuckGo Search
- Streamlit

## 📁 Project Structure

```
.
├── agent.py            # Agent + terminal chat
├── app.py              # Streamlit web app
├── requirements.txt    # Dependencies
└── .env                # Your API key (not committed)
```

## 🚀 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Mariasrh/week3.git
   cd week3
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file at the root of the project:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

   Get a free key at [console.groq.com](https://console.groq.com/keys).

## 💬 Usage

**Web app:**

```bash
streamlit run app.py
```

**Terminal chat:**

```bash
python agent.py
```

Then type something like: *"I have chicken, rice and carrots"*.

## 👩‍💻 Author

**Mariasrh**, project made during my training with **THIRDUNI**.

