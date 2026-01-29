# 🎙️ Voice Conversation Practice - Complete Guide

This guide covers the Voice Conversation Practice feature in Polyglot - an automatic voice-to-voice conversation system with AI.

## 🌟 What Is It?

Voice Conversation Practice lets you have natural spoken conversations with the AI in your target language. You speak, it transcribes, the AI responds, and speaks back - automatically!

### Key Features
- 🎤 **Speak naturally** - Just talk like you would to a person
- 📝 **Auto-transcription** - Uses Whisper to convert speech to text
- 🤖 **AI conversations** - Natural back-and-forth dialogue
- 🔊 **AI speaks back** - Uses edge-tts for natural voice responses
- 🔄 **Continuous mode** - Keep chatting without manual resets
- 💰 **Free options** - Use Ollama for completely free local AI

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Or install voice-specific packages:
pip install faster-whisper streamlit-audiorecorder edge-tts
```

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Go to Speech Practice Tab

Click on the **"🎙️ Speech Practice"** tab in the app.

---

## 📖 How to Use

### Starting a Voice Conversation

1. **Click the big purple button:** "🎤 Start Voice Conversation"
2. **Header turns green** - You're now in listening mode
3. **Tap the microphone button** that says "🔴 Tap to speak"
4. **Speak** in your target language
5. **Tap the button again** when you're done
6. **Watch the magic:**
   - 🎙️ Transcribing your speech...
   - 💬 Adding your message...
   - 🤖 AI is thinking...
   - 🔊 Generating voice response...
   - ✅ Done! Speak again...
7. **AI voice plays automatically!** 🔊
8. **Speak again** - The recorder is ready!

### Stopping the Conversation

Click the **"⏹️ Stop"** button when you want to end the voice session.

---

## ⚙️ Settings & Controls

### When Voice Session is Active

Three controls appear:

| Button | Function |
|--------|----------|
| **⏹️ Stop** | End the voice conversation session |
| **Model** | Choose Whisper model size (tiny/base/small/medium) |
| **🗑️ Clear** | Clear conversation history |

### Whisper Model Selection

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| **Tiny** | 39M | ⚡⚡⚡ Fastest | Clear speech, quick conversations |
| **Base** | 74M | ⚡⚡ Very fast | Good balance |
| **Small** | 244M | ⚡ Balanced | Most use cases |
| **Medium** | 769M | 🐢 Slower | Better accuracy |
| **Large** | 1.5B | 🐢🐢 Slowest | Best accuracy |

**Recommendation:** Start with **Tiny** or **Base** for fastest response!

---

## 🎯 Tips for Best Results

### Speaking Tips
- ✅ **Speak clearly** at a natural pace
- ✅ **Keep it short** - 1-2 sentences per message
- ✅ **Use simple vocabulary** appropriate for your level
- ✅ **Minimize background noise**
- ❌ **Don't rush** - take your time

### Conversation Topics
- Greetings and introductions
- Talking about your day
- Describing your hobbies
- Asking about the culture
- Ordering food (role-play)
- Asking for directions

### What to Say
**Start with:**
- "Hello, how are you?"
- "My name is..."
- "I'm learning [language]"
- "How do you say..."

**Then move to:**
- "Tell me about..."
- "What do you think about..."
- "Can you help me with..."
- "How do I say..."

---

## 🔧 Under the Hood

### How It Works

```
Your Voice → faster-whisper → Text → AI (Ollama/OpenAI) → Response → edge-tts → Audio → Auto-play
```

1. **Speech Recognition** (faster-whisper)
   - Converts your audio to text
   - Uses VAD (Voice Activity Detection) to remove silence
   - Language-specific models for accuracy

2. **AI Processing** (Your chosen model)
   - Understands your message
   - Generates natural response
   - Adapts to your CEFR level
   - Responds in target language only

3. **Text-to-Speech** (edge-tts)
   - Microsoft Edge neural voices
   - Natural-sounding speech
   - Language-specific voice models
   - Auto-plays when ready

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Speech-to-Text** | faster-whisper | Transcribe your voice |
| **LLM** | Ollama/OpenAI | Generate responses |
| **Text-to-Speech** | edge-tts | Generate AI voice |
| **Audio Recording** | streamlit-audiorecorder | Browser recording |

---

## 🆚 Model Options

### Option 1: Ollama (Free, Local)

**Pros:**
- ✅ Completely free
- ✅ Runs locally (privacy)
- ✅ No API key needed
- ✅ Works offline
- ❌ Requires decent computer
- ❌ Need to install Ollama

**Setup:**
```bash
# Install Ollama
curl https://ollama.com/install.sh | sh

# Pull a model
ollama pull qwen3:0.6b

# Start Ollama
ollama serve
```

**In the app:**
- Sidebar → AI Model Selection → Choose "ollama"
- Select your model

### Option 2: OpenAI (Paid, Cloud)

**Pros:**
- ✅ No installation needed
- ✅ Works on any computer
- ✅ Fast and reliable
- ❌ Costs money
- ❌ Requires API key

**Setup:**
```bash
# Create .streamlit/secrets.toml
OPENAI_API_KEY="your-key-here"
```

**In the app:**
- Sidebar → AI Model Selection → Choose "openai"

---

## 🐛 Troubleshooting

### Common Issues

**1. "⚠️ Install: pip install streamlit-audiorecorder"**
```bash
pip install streamlit-audiorecorder
```

**2. "❌ edge-tts not installed"**
```bash
pip install edge-tts
```

**3. "❌ Transcription error"**
- Make sure faster-whisper is installed
- First run downloads the model (be patient)
- Try a smaller model (tiny or base)

**4. "❌ TTS error"**
- Check internet connection (edge-tts needs internet)
- Try again

**5. "AI won't respond"**
- Check if Ollama is running: `ollama serve`
- Or check your OpenAI API key

**6. "Audio won't play"**
- Check browser console for errors
- Make sure autoplay is not blocked by browser

**7. "Recorder resets too quickly"**
- This is normal! After processing, it's ready for your next message
- Just tap and speak again

---

## 💡 Advanced Usage

### Improving Accuracy

**For Speech Recognition:**
- Speak close to microphone
- Use a quiet environment
- Try larger Whisper models (medium/large)
- Speak at moderate pace

**For AI Responses:**
- Use larger models (phi3 instead of qwen3:0.6b)
- Be specific in your requests
- Ask follow-up questions

### Optimizing Speed

**Want faster responses?**
- Use **Tiny** or **Base** Whisper model
- Use **qwen3:0.6b** or **gemma2:2b** Ollama models
- Keep messages short (1 sentence)

**Want better quality?**
- Use **Small** or **Medium** Whisper model
- Use **phi3** Ollama model
- Speak clearly and slowly

---

## 🎓 Example Conversations

### Finnish (A1 Level)

```
You: "Hyvää huomenta"
AI: "Hyvää huomenta! Kuinka voit?"
You: "Voin hyvin, kiitos. Sinä?"
AI: "Minä voin hyvin, kiitos! Mitä haluaisit keskustella?"
```

### Spanish (A2 Level)

```
You: "Me llamo Juan"
AI: "¡Mucho gusto, Juan! ¿De dónde eres?"
You: "Soy de México"
AI: "¡Qué interesante! ¿Qué te gusta hacer en tu tiempo libre?"
```

### French (B1 Level)

```
You: "J'aimerais pratiquer le français"
AI: "C'est une excellente idée! Quels sujets t'intéressent?"
You: "J'aime parler de voyages et de culture"
AI: "Moi aussi! Tu es déjà allé dans des pays francophones?"
```

---

## 📊 Comparison with Other Methods

| Method | Cost | Privacy | Speed | Naturalness |
|--------|------|---------|-------|--------------|
| **Polyglot Voice** | Free/Low | ✅ Local/Cloud | Fast | ⭐⭐⭐⭐⭐ |
| **ChatGPT Plus Voice** | Paid | ❌ Cloud | Fast | ⭐⭐⭐⭐⭐ |
| **Human Tutor** | Expensive | ✅ In-person | Varies | ⭐⭐⭐⭐⭐ |
| **Textbooks** | Free | ✅ N/A | Self-paced | ⭐⭐ |
| **Language Apps** | Freemium | ❌ Cloud | Fast | ⭐⭐⭐ |

---

## 🎉 Getting Started Example

Here's your first voice session:

### Step 1: Start
```
1. Open app
2. Select "Finnish" (or your target language)
3. Select "A1" (Beginner)
4. Click "🎙️ Speech Practice" tab
5. Click "🎤 Start Voice Conversation"
```

### Step 2: First Message
```
1. Tap "🔴 Tap to speak"
2. Say: "Hyvää huomenta" (Good morning)
3. Tap again
4. Wait for processing...
5. AI says: "Hyvää huomenta! Kuinka voit?"
```

### Step 3: Respond
```
1. Tap microphone again
2. Say: "Voin hyvin" (I'm fine)
3. Tap again
4. Continue the conversation!
```

---

## 🔄 Continuous Conversation Flow

```
┌─────────────────────────────────────────────────────┐
│  You speak → Stop recording → Processing...          │
│                                                         │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐           │
│  │  🎙️    │ → │  🤖     │ → │  🔊     │           │
│  │Transcribe│   │  Think  │   │  Speak  │           │
│  └─────────┘   └─────────┘   └─────────┘           │
│                                                         │
│  Ready for your next message! ✓                      │
└─────────────────────────────────────────────────────┘
```

---

## 🌟 Pro Tips

1. **Start simple** - Begin with greetings and basic phrases
2. **Be patient** - First run downloads models (cached after)
3. **Use headphones** - Better audio quality
4. **Practice daily** - 15 minutes of voice practice daily
5. **Review the chat** - Read the text to see what was said
6. **Don't worry** - Mistakes are part of learning!

---

## 📚 Additional Resources

- [CEFR Level Descriptions](https://www.coe.int/en/web-portfolio/for-the-common-european-framework-of-reference-for-languages-learning-teaching-assessment)
- [Ollama Documentation](https://ollama.com/docs)
- [edge-tts Documentation](https://github.com/rany2/edge-tts)
- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)

---

**Ready to practice? Start your voice conversation now!** 🎙️✨

Made with ❤️ for language learners who want to speak confidently.
