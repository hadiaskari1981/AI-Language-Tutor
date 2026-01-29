# 🌍 Polyglot - Multilingual Learning Assistant

An AI-powered language learning tutor that adapts to your proficiency level and helps you learn multiple languages through conversation, exercises, and voice practice.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎯 Core Features
- **Adaptive Learning** - Content adapts to your CEFR level (A1-C1)
- **7 Languages Supported** - Finnish, Spanish, French, German, Italian, Russian, Swedish
- **AI Tutor Chat** - Natural conversations with explanations and exercises
- **File Upload** - Learn from documents, images, and any text files
- **Grammar Explanations** - Language-specific grammar rules and examples
- **Translation** - Instant translations between your target language and English

### 🎙️ Voice Conversation Practice (NEW!)
- **Speak Naturally** - Have voice conversations with the AI
- **Auto-Transcription** - Uses Whisper (faster-whisper) for speech-to-text
- **AI Speaks Back** - Natural text-to-speech using edge-tts (Microsoft Edge)
- **Continuous Chat** - Keep the conversation going with automatic resets
- **Model Selection** - Choose from Tiny to Large Whisper models

### 🤖 Model Flexibility
- **OpenAI Models** - Use GPT models (requires API key)
- **Ollama Models** - Free local models (phi3, gemma2:2b, llama3.2:1b, qwen2.5:3b, etc.)
- **Easy Switching** - Toggle between providers in the sidebar

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Polyglot-Multilingual-Learning-Assistant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up OpenAI API key (optional - for OpenAI models):**
```bash
# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Create or edit .streamlit/secrets.toml
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY="your-openai-api-key-here"
MODEL_NAME="gpt-4.1-mini-2025-04-14"
EOF
```

4. **Run the application:**
```bash
streamlit run app.py
```

5. **Open your browser:**
```
http://localhost:8501
```

## 📖 Usage Guide

### Getting Started

1. **Select Your Language**
   - Choose from the sidebar: Finnish, Spanish, French, German, Italian, Russian, or Swedish

2. **Choose Your Level**
   - Pick your CEFR level: A1 (Beginner) to C1 (Advanced)
   - All content will adapt to your level

3. **Start Chatting**
   - Type your questions or requests
   - Upload files to learn from
   - Ask for translations, grammar help, or exercises

### 🎙️ Voice Conversation Mode

The new Voice Conversation feature lets you speak naturally with AI feedback:

1. **Click "Start Voice Conversation"** button
2. **Tap the microphone** and speak in your target language
3. **Tap again** when you're done speaking
4. **AI responds** with voice automatically!
5. **Keep chatting** - The recorder resets for your next message

#### Voice Mode Settings
- **Transcription Model**: Choose Tiny (fastest) to Large (most accurate)
- **Stop**: End the voice session
- **Clear**: Reset conversation history

### 🆚 Using Ollama (Free Local Models)

Ollama provides free, local AI models - no API key needed!

1. **Install Ollama:**
   ```bash
   # Linux
   curl https://ollama.com/install.sh | sh

   # macOS
   brew install ollama

   # Windows
   # Download from https://ollama.com/download
   ```

2. **Pull a model:**
   ```bash
   # Pull a small model (recommended)
   ollama pull qwen3:0.6b

   # Or pull other models
   ollama pull phi3
   ollama pull gemma2:2b
   ollama pull llama3.2:1b
   ```

3. **Start Ollama:**
   ```bash
   ollama serve
   ```

4. **In the app sidebar:**
   - Under "AI Model Selection", choose "ollama"
   - Select your model from the dropdown

### 📁 File Upload

Upload any file to learn from its content:
- **Text files** (.txt, .md, .csv, .json, etc.)
- **Documents** (.pdf, .docx, etc.)
- **Images** - Extract text from images
- The AI will create exercises based on the file content

## 🌐 Supported Languages

| Language | Code | Flag | Native Name |
|----------|------|------|-------------|
| Finnish | fin | 🇫🇮 | Suomi |
| Spanish | spa | 🇪🇸 | Español |
| French | fra | 🇫🇷 | Français |
| German | deu | 🇩🇪 | Deutsch |
| Italian | ita | 🇮🇹 | Italiano |
| Russian | rus | 🇷🇺 | Русский |
| Swedish | swe | 🇸🇪 | Svenska |

## 📚 CEFR Levels Explained

| Level | Description | Can |
|-------|-------------|-----|
| **A1** | Beginner | Basic phrases, simple sentences |
| **A2** | Elementary | Everyday routines, simple communication |
| **B1** | Intermediate | Main points of familiar matters, connected text |
| **B2** | Upper Intermediate | Complex text, spontaneous interaction with natives |
| **C1** | Advanced | Demanding texts, fluent and spontaneous expression |

## 🔧 Configuration

### OpenAI API Configuration

Edit `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY="sk-proj-..."
MODEL_NAME="gpt-4.1-mini-2025-04-14"
MAX_TOKENS=8000
```

### Model Selection

**OpenAI Models:**
- gpt-4.1-mini-2025-04-14 (recommended, cost-effective)
- gpt-4o
- gpt-4o-mini
- gpt-3.5-turbo

**Ollama Models (Free):**
- qwen3:0.6b (fastest, 600M parameters)
- phi3 (3.8B) - balanced
- gemma2:2b (2B) - very fast
- llama3.2:1b (1B) - smallest
- qwen2.5:3b (3B) - efficient

## 📦 Requirements

```
streamlit>=1.20.0
langchain>=0.1.0
langchain-openai>=0.1.0
langchain-ollama>=0.1.0
openai>=1.0.0
python-dotenv>=1.0.0
Pillow>=10.0.0
pydub>=0.25.0
faster-whisper>=1.0.0
streamlit-audiorecorder>=0.1.0
edge-tts>=6.1.0
```

## 🎯 Features in Detail

### Exercise Types

1. **Reading Exercises** - Stories and situations at your level
2. **Vocabulary Exercises** - Learn and practice new words
3. **Writing Exercises** - Translate text into your target language
4. **Quizzes** - Test your knowledge with interactive questions

### Conversation Features

- **Time-based greetings** - Different greetings for morning/afternoon/evening
- **Language switching** - Change language mid-conversation
- **Level progression** - Track your journey across CEFR levels
- **Chat history export** - Download conversations as Markdown

## 🔮 Upcoming Features

These features are marked as "coming soon" and will be implemented in future releases:

- 📊 **Progress Analytics** - Track learning with detailed stats
- 👥 **Language Community** - Connect with other learners
- 📚 **Content Library** - Curated reading materials
- 📱 **Mobile App** - Learn on the go with offline mode
- 🌐 **Immersive Learning** - Virtual scenarios and simulations

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API Key Error**
```
Error: OpenAI API key not configured
```
**Solution:** Add your API key to `.streamlit/secrets.toml`

**2. Ollama Connection Error**
```
Error connecting to Ollama
```
**Solution:** Make sure Ollama is running with `ollama serve`

**3. Whisper Model Download**
```
Downloading Whisper model...
```
**First run only:** This happens once per model size. Downloads are cached.

**4. Voice Recording Not Working**
```
⚠️ Install: pip install streamlit-audiorecorder
```
**Solution:** Install with `pip install streamlit-audiorecorder`

**5. TTS Error**
```
❌ edge-tts not installed
```
**Solution:** Install with `pip install edge-tts`

### Performance Tips

- **Faster transcription**: Use "tiny" or "base" Whisper models
- **Faster AI responses**: Use smaller Ollama models (qwen3:0.6b)
- **Less memory**: Use "int8" quantization (enabled by default)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Streamlit** - The web framework
- **LangChain** - LLM orchestration
- **faster-whisper** - Fast speech recognition
- **edge-tts** - Text-to-speech synthesis
- **OpenAI** - GPT models
- **Ollama** - Local LLM runtime

---

**Made with ❤️ for language learners worldwide**

Start your multilingual journey today! 🌍✨
