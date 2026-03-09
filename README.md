# 🗣️ AI Language Learning Assistant

A conversational language-learning application powered by modern AI models. The system adapts exercises, explanations, and dialogue to the learner’s proficiency level, enabling practice through text, voice, and interactive activities.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)

---

# Overview

This project provides an interactive tutor capable of helping users study multiple languages through dialogue, grammar explanations, exercises, and voice interaction. The application adjusts difficulty according to CEFR levels and allows flexible use of either cloud-based or locally hosted language models.

---

# Main Capabilities

## Adaptive Learning System

- **Level-aware instruction** aligned with CEFR levels (A1 → C1)
- **Multi-language support** across several European languages
- **Conversational AI tutor** for real-time interaction
- **Grammar explanations** tailored to the target language
- **Instant translation** between English and the selected language
- **File-based learning** using uploaded documents or images

## Voice-Based Practice

The application also supports spoken interaction with the tutor.

- **Natural speech input**
- **Speech transcription** via Whisper (faster-whisper)
- **AI voice responses** using Edge TTS
- **Continuous voice conversation**
- **Configurable transcription models** (Tiny → Large)

This enables realistic conversation training without requiring manual typing.

## Model Flexibility

Users can choose between different model providers:

### Cloud Models
- OpenAI GPT models (API key required)

### Local Models
- Models executed locally using Ollama  
- Examples include:
  - phi3
  - gemma2
  - llama3
  - qwen variants

The model provider can be switched directly from the interface.

---

# Quick Setup

## Requirements

- Python **3.8 or newer**
- pip package manager

---

## Installation Steps

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI-Language-Tutor
