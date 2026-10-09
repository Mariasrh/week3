import os
from dotenv import load_dotenv
from groq import Groq

# Load .env file containing GROQ_API_KEY
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    # Fetch all available models from Groq
    models = client.models.list()
    print("=== AVAILABLE GROQ MODELS ===")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"Error fetching models: {e}")