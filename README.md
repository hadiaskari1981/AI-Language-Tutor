# AI Language Tutor

An adaptive AI-powered language learning assistant built with Streamlit. Adjusts instruction style, vocabulary, and grammar explanations to the learner's CEFR proficiency level in real time. Supports both cloud-based (OpenAI) and fully local (Ollama) LLM backends.

## Features

- **CEFR-adaptive tutoring** — instruction calibrated to levels A1 through C1, with level-aware prompting for grammar, vocabulary, and exercises
- **Voice interaction** — speech input via Whisper (faster-whisper), AI voice responses via Edge TTS; full voice conversation loop
- **Multi-language support** — Finnish, Spanish, French, German, Italian, Russian, Swedish
- **File-based learning** — upload documents or images for context-aware practice
- **Flexible LLM backend** — switch between OpenAI GPT models and local Ollama models (phi3, gemma2, llama3, qwen) from the UI

## Stack

- **Frontend**: Streamlit
- **LLM Orchestration**: LangChain (`langchain-openai`, `langchain-ollama`)
- **Speech-to-Text**: faster-whisper (Whisper models: tiny → large)
- **Text-to-Speech**: Edge TTS with language-native neural voices
- **Local LLM**: Ollama

## How It Works

```
User input (text or voice)
        ↓
Whisper transcription (if voice)
        ↓
LangChain prompt — CEFR level + target language injected into system prompt
        ↓
LLM (OpenAI API or local Ollama)
        ↓
Response displayed + optionally spoken via Edge TTS
```

The system prompt encodes the full CEFR framework: at A1 the tutor uses only basic vocabulary and present tense; at C1 it uses full grammatical structures and literary language.

## Run Locally

**Prerequisites:** Python 3.10+, and either an OpenAI API key or [Ollama](https://ollama.ai) installed locally.

```bash
git clone https://github.com/hadiaskari1981/AI-Language-Tutor
cd AI-Language-Tutor
pip install -r requirements.txt
```

For OpenAI backend, create a `.env` file:
```
OPENAI_API_KEY=your_key_here
```

For local Ollama backend, pull a model first:
```bash
ollama pull phi3
```

Then start the app:
```bash
streamlit run app.py
```

## Project Structure

```
├── app.py               # Streamlit UI, session state, language config
├── chatbot.py           # LangChain chain, CEFR-adaptive system prompt
├── speech_practice.py   # Whisper transcription, Edge TTS voice output
├── utils.py             # File upload processing, level badge rendering
└── requirements.txt
```
