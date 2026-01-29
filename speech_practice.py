"""
Speech Practice Module - Automatic voice conversation like ChatGPT
"""

import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime
import io
import tempfile
import os
import base64


def transcribe_audio(audio_bytes, language_code: str = "fin", model_size: str = "tiny") -> Optional[str]:
    """Transcribe audio using faster-whisper."""
    try:
        from faster_whisper import WhisperModel

        whisper_language_map = {
            "fin": "fi", "spa": "es", "fra": "fr",
            "deu": "de", "ita": "it", "rus": "ru", "swe": "sv"
        }

        whisper_lang = whisper_language_map.get(language_code, "fi")

        with st.spinner(f"🔄 Loading model..."):
            model = WhisperModel(model_size, device="cpu", compute_type="int8")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name

        try:
            with st.spinner("🎙️ Transcribing..."):
                segments, _ = model.transcribe(
                    temp_file_path,
                    language=whisper_lang,
                    beam_size=5,
                    vad_filter=True
                )
                transcription_text = " ".join([s.text for s in segments]).strip()
            return transcription_text
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def audiosegment_to_wav_bytes(audio_segment) -> bytes:
    """Convert AudioSegment to WAV bytes."""
    wav_io = io.BytesIO()
    audio_segment.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io.read()


def text_to_speech(text: str, language_code: str) -> Optional[str]:
    """Convert text to speech using edge-tts."""
    try:
        import edge_tts
        import asyncio

        voice_map = {
            "fin": "fi-FI-SelmaNeural", "spa": "es-ES-ElviraNeural",
            "fra": "fr-FR-DeniseNeural", "deu": "de-DE-KatjaNeural",
            "ita": "it-IT-ElsaNeural", "rus": "ru-RU-SvetlanaNeural",
            "swe": "sv-SE-SofieNeural"
        }

        voice = voice_map.get(language_code, "fi-FI-SelmaNeural")
        communicate = edge_tts.Communicate(text, voice)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        asyncio.run(communicate.save(temp_path))
        return temp_path
    except Exception as e:
        st.error(f"❌ TTS error: {str(e)}")
        return None


def get_auto_audio_html(audio_path: str) -> str:
    """Generate auto-playing audio HTML."""
    with open(audio_path, 'rb') as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()

    return f"""
    <audio autoplay style="width: 100%; margin-top: 10px;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
    </audio>
    """


def get_conversation_response(user_message: str, session_state) -> str:
    """Get AI response."""
    try:
        from chatbot import get_llm, get_language_display_name

        chat = get_llm(session_state, streaming=False)
        level_code = session_state.selected_level.split()[0]
        lang_code = session_state.selected_language
        lang_name = get_language_display_name(lang_code)

        prompt = f"""Have a friendly conversation with a {lang_name} learner at {level_code} level.

Learner said: "{user_message}"

Respond naturally in {lang_name}:
- Keep responses appropriate for {level_code}
- Be encouraging and friendly
- Ask follow-up questions
- Keep it concise (2-3 sentences)
- Respond ONLY in {lang_name}"""

        response = chat.invoke([
            {"role": "system", "content": f"You are a helpful {lang_name} conversation partner."},
            {"role": "user", "content": prompt}
        ])
        return response.content
    except Exception as e:
        return f"Sorry, couldn't respond: {str(e)}"


def render_speech_practice_tab(session_state):
    """Render automatic voice conversation interface."""

    # Initialize session state
    if 'voice_chat_messages' not in session_state:
        session_state.voice_chat_messages = []
    if 'whisper_model_size' not in session_state:
        session_state.whisper_model_size = "tiny"
    if 'voice_session_active' not in session_state:
        session_state.voice_session_active = False
    if 'recording_iteration' not in session_state:
        session_state.recording_iteration = 0

    # CSS for beautiful UI
    st.markdown("""
    <style>
        .voice-active {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            animation: glow 2s ease-in-out infinite alternate;
        }
        .voice-inactive {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(76, 175, 80, 0.4); }
            to { box-shadow: 0 0 40px rgba(76, 175, 80, 0.8); }
        }
        @keyframes pulse-ring {
            0% { transform: scale(0.8); opacity: 1; }
            100% { transform: scale(1.3); opacity: 0; }
        }
        .recording-indicator::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: rgba(255, 0, 0, 0.3);
            animation: pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
        }
        .chat-bubble-user {
            background: linear-gradient(135deg, #2196F3, #1976D2);
            color: white;
            padding: 14px 18px;
            border-radius: 20px 20px 4px 20px;
            max-width: 75%;
            margin-left: auto;
            box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
        }
        .chat-bubble-ai {
            background: white;
            color: #333;
            padding: 14px 18px;
            border-radius: 20px 20px 20px 4px;
            max-width: 75%;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # Main status card
    is_active = session_state.voice_session_active

    st.markdown(f"""
    <div class="{'voice-active' if is_active else 'voice-inactive'}"
         style="padding: 3rem 2rem; border-radius: 20px; margin-bottom: 2rem;
                color: white; text-align: center; position: relative;">
        <div style="position: relative; display: inline-block;">
            <h1 style="margin: 0 0 1rem 0; font-size: 2.5rem;">
                {'🎙️🔊 Listening...' if is_active else '🎙️ Voice Chat'}
            </h1>
        </div>
        <p style="margin: 0; font-size: 1.2rem; opacity: 0.95;">
            {('Speak now and I\'ll respond automatically!' if is_active
              else 'Click the button below to start voice conversation')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Single prominent toggle button
    if not is_active:
        if st.button("🎤 Start Voice Conversation", type="primary", use_container_width=True):
            session_state.voice_session_active = True
            st.rerun()
    else:
        # When active, show controls in a clean row
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⏹️ Stop", type="secondary", use_container_width=True):
                session_state.voice_session_active = False
                st.rerun()
        with col2:
            model_size = st.selectbox(
                "Model",
                ["tiny", "base", "small", "medium"],
                index=["tiny", "base", "small", "medium"].index(session_state.whisper_model_size),
                label_visibility="collapsed"
            )
            session_state.whisper_model_size = model_size
        with col3:
            if st.button("🗑️ Clear", use_container_width=True):
                session_state.voice_chat_messages = []
                session_state.recording_iteration = 0
                st.rerun()

    st.markdown("---")

    # Chat display
    if session_state.voice_chat_messages:
        for msg in session_state.voice_chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-bubble-user">
                    🎤 {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-bubble-ai">
                    🤖 {msg['content']}
                </div>
                """, unsafe_allow_html=True)
                if 'audio_path' in msg and msg['audio_path']:
                    st.markdown(get_auto_audio_html(msg['audio_path']), unsafe_allow_html=True)
    else:
        if not is_active:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fff3e0, #ffe0b2);
                        padding: 3rem; border-radius: 16px; text-align: center;
                        border: 2px dashed #FF9800;">
                <h3 style="color: #E65100; margin: 0 0 1rem 0;">🎤 Ready to Chat!</h3>
                <p style="margin: 0; color: #666; font-size: 1.1rem;">
                    Click "Start Voice Conversation" above to begin speaking with AI
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Voice input (only when active)
    if is_active:
        st.markdown("---")
        st.markdown("### 🎙️ Speak Now")

        try:
            from audiorecorder import audiorecorder

            # Recording with auto-detection of new audio
            audio = audiorecorder(
                "🔴 Tap to speak",
                key=f"voice_{session_state.recording_iteration}"
            )

            if audio is not None and len(audio) > 0:
                # Process automatically
                audio_bytes = audiosegment_to_wav_bytes(audio)

                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("🎙️ Transcribing your speech...")
                progress_bar.progress(25)

                transcribed = transcribe_audio(
                    audio_bytes,
                    session_state.selected_language,
                    model_size=session_state.whisper_model_size
                )

                if transcribed:
                    status_text.text("💬 Adding your message...")
                    progress_bar.progress(50)

                    session_state.voice_chat_messages.append({
                        "role": "user",
                        "content": transcribed,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

                    status_text.text("🤖 AI is thinking...")
                    progress_bar.progress(75)

                    ai_response = get_conversation_response(transcribed, session_state)

                    session_state.voice_chat_messages.append({
                        "role": "assistant",
                        "content": ai_response,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

                    status_text.text("🔊 Generating voice response...")
                    progress_bar.progress(90)

                    audio_path = text_to_speech(ai_response, session_state.selected_language)

                    if audio_path:
                        session_state.voice_chat_messages[-1]['audio_path'] = audio_path

                    progress_bar.progress(100)
                    status_text.text("✅ Done! Speak again...")

                    # Increment to reset recorder
                    session_state.recording_iteration += 1

                    # Auto-rerun after a short delay
                    import time
                    time.sleep(1)
                    st.rerun()

        except ImportError:
            st.error("⚠️ Please install: `pip install streamlit-audiorecorder`")
            session_state.voice_session_active = False
            st.rerun()

    # Tips (collapsed)
    with st.expander("💡 How it works", expanded=False):
        st.markdown("""
        **Automatic Voice Conversation:**
        1. Click **"Start Voice Conversation"**
        2. Tap the microphone and speak
        3. Tap again when done
        4. AI transcribes, thinks, and speaks back automatically
        5. Ready for your next message immediately!

        **Tips:**
        - Speak clearly at a natural pace
        - Keep messages short (1-2 sentences)
        - The conversation flows automatically!
        """)
