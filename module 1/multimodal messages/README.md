# LangChain Multimodal Demo: Image Analysis & Audio Prompt-Injection Test

A Jupyter notebook exploring **multimodal inputs** with LangChain and Groq. It has two interactive experiments built with `ipywidgets`: asking a vision model about **small details in an uploaded image**, and testing how an LLM reacts to **instructions hidden inside an audio message**.

> 🎓 **Note:** This code was written during my training with **ThirdUni**.

---

## What the Notebook Covers

| Task | Input | What it does |
|------|-------|--------------|
| **Task 1: Detail extraction** | Image (`.jpg`, `.jpeg`, `.png`) | Resizes the image, sends it to a vision model with a targeted question, and prints the answer. |
| **Task 2: Audio prompt injection test** | Audio (`.mp3`, `.wav`) | Transcribes the audio with Whisper, then asks the LLM to summarize the transcription. |

### Task 1: Multimodal Specific Detail Extraction

1. The user uploads an image with a file upload widget and clicks **Analyze Detail**.
2. The image is opened with Pillow and **resized** (max 1024 px, JPEG quality 85) to avoid `413 Payload Too Large` errors.
3. A preview is displayed, then the image is converted to **Base64**.
4. A `HumanMessage` combining a text question and the image (`image_url` with a data URI) is sent to the model.
5. The question asks for **small background details**: buildings, skyscrapers or landmarks visible in the far distance, with their shapes and features.

### Task 2: Audio Prompt Injection Test

1. The user uploads an audio clip and clicks **Test Audio Injection**.
2. An audio player preview is displayed.
3. The audio is transcribed with **Whisper** (`whisper-large-v3`) through the Groq API.
4. The transcription is inserted into a prompt asking the LLM to **summarize the voice message**.
5. The goal is to observe whether instructions spoken in the audio (for example "ignore previous instructions...") influence the agent's behavior.

## Project Structure

```
.
├── multimodal.ipynb    # The notebook
├── .env                # API keys (not committed)
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
   pip install python-dotenv langchain-core langchain-groq groq pillow ipywidgets jupyter
   ```

   The first cell of the notebook also runs `!pip install ipywidgets`.

3. **Configure your environment variables**

   Create a `.env` file next to the notebook:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

```bash
jupyter notebook multimodal.ipynb
```

Run the cells from top to bottom, then use the widgets:

- **Task 1:** upload an image (for example a photo of a monument with a city in the background), click **Analyze Detail** and read the model's description of the background.
- **Task 2:** upload a short `.mp3` or `.wav` recording, click **Test Audio Injection** and compare the transcription with the summary produced by the agent.

## How It Works

```
Task 1                                   Task 2
Image upload                             Audio upload
    │                                        │
    ▼                                        ▼
Pillow resize (max 1024 px)              Whisper transcription (Groq)
    │                                        │
    ▼                                        ▼
Base64 data URI                          Transcript inserted in the prompt
    │                                        │
    ▼                                        ▼
HumanMessage [text + image_url]          HumanMessage [text only]
    │                                        │
    ▼                                        ▼
ChatGroq  ──► answer                     ChatGroq  ──► summary
```

## Key Takeaways

- A LangChain `HumanMessage` can carry **mixed content**: a list of text and image parts.
- **Resizing images** before sending them reduces payload size and avoids API errors, while keeping enough detail for the model.
- Audio is not sent to the LLM directly here: it is first converted to text (speech-to-text), which then becomes part of the prompt.
- **Prompt injection can come from any input type.** Text produced from audio is untrusted content, and an LLM may follow instructions hidden in it.

## Notes

- The vision question in Task 1 is fixed and focused on background details. It can be changed to test other kinds of questions.
- Both experiments use `qwen/qwen3.8-27b`. Task 1 requires a model that accepts image input, so if you get an error, check which vision-capable models are available on your Groq account and update the model name.
- In Task 2, the transcription is inserted directly into the prompt. To reduce injection risk, clearly separate untrusted content from instructions (for example with delimiters and an explicit instruction to treat it as data only), and never give the agent powerful tools when it processes untrusted input.
- Audio files may be subject to size limits on the Whisper API.
- The widgets need an environment that supports `ipywidgets` (they are displayed as widget views in the saved notebook outputs).
- Never commit your `.env` file. Add it to `.gitignore`.

## Technologies

- [Python](https://www.python.org/) and [Jupyter](https://jupyter.org/)
- [LangChain](https://www.langchain.com/)
- [Groq](https://groq.com/) (LLM and Whisper)
- [Pillow](https://python-pillow.org/)
- [ipywidgets](https://ipywidgets.readthedocs.io/)

## Acknowledgments

Built as part of my training with **ThirdUni**. Thanks to the instructors and the community for the guidance.
