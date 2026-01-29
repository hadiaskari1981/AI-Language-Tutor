import streamlit as st
from datetime import datetime
import uuid
import base64

# Import from other modules
from chatbot import process_question, get_chat_history_markdown
from utils import process_uploaded_file, get_level_color, format_level_badge
from speech_practice import render_speech_practice_tab

# Configure page
st.set_page_config(
    page_title="Language Learning Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Base styling */
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Chat message styling */
    .chat-message {
    .chat-message {🌍
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 0.75rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .chat-message.user {
        background-color: #e6f7ff;
        margin-left: 2rem;
    }
    .chat-message.assistant {
        background-color: #f0f2f5;
        margin-right: 2rem;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }
    .chat-message .message {
        flex: 1;
    }
    
    /* Input elements styling */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        background-color: #0066FF;
        color: white;
        font-weight: bold;
        width: 100%;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 5px;
        line-height: 1.2;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0052cc;
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #f0f2f5;
        padding: 2rem 1rem;
    }
    .sidebar-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
        color: #0066FF;
    }
    
    /* Welcome card styling */
    .welcome-card {
        background-color: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        border-top: 4px solid #0066FF;
    }
    .welcome-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .welcome-icon {
        font-size: 2.5rem;
        margin-right: 1rem;
    }
    
    /* File upload styling */
    .uploadedFile {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        background-color: #f9f9f9;
    }
    
    /* Level selection styling */
    .level-select {
        margin-bottom: 1rem;
        border-radius: 8px;
    }

    /* Level badge styling */
    .level-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: bold;
        font-size: 0.9rem;
        margin-right: 0.5rem;
        color: white;
    }
    .level-badge.A1 {
        background-color: #4CAF50;
    }
    .level-badge.A2 {
        background-color: #8BC34A;
    }
    .level-badge.B1 {
        background-color: #2196F3;
    }
    .level-badge.B2 {
        background-color: #3F51B5;
    }
    .level-badge.C1 {
        background-color: #9C27B0;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .chat-message {
            padding: 1rem;
            margin-left: 0.5rem;
            margin-right: 0.5rem;
        }
        .welcome-card {
            padding: 1.5rem;
        }
        .stButton > button {
            font-size: 14px;
        }
    }
    
    /* Grammar tables styling */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9em;
        font-family: sans-serif;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        border-radius: 8px;
        overflow: hidden;
    }
    thead tr {
        background-color: #0066FF;
        color: #ffffff;
        text-align: left;
    }
    th, td {
        padding: 12px 15px;
    }
    tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }
    tbody tr:last-of-type {
        border-bottom: 2px solid #0066FF;
    }
    
    /* Level-specific background styles */
    .level-bg-A1 {
        background-color: rgba(76, 175, 80, 0.1);
    }
    .level-bg-A2 {
        background-color: rgba(139, 195, 74, 0.1);
    }
    .level-bg-B1 {
        background-color: rgba(33, 150, 243, 0.1);
    }
    .level-bg-B2 {
        background-color: rgba(63, 81, 181, 0.1);
    }
    .level-bg-C1 {
        background-color: rgba(156, 39, 176, 0.1);
    }
    
    /* Custom title styling */
    .main-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Language flag styling */
    .language-flag {
        vertical-align: middle;
        margin-right: 5px;
    }
    
    /* Future features styles */
    .features-heading {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 25px 0 15px 0;
        color: #333;
    }
    
    /* Coming soon container styles */
    .coming-soon-container {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        border: 1px dashed #FF9800;
        background-color: #FFF8E1;
    }
    
    .coming-soon-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        color: #FF9800;
    }
    
    .coming-soon-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #FF9800;
    }
    
    .coming-soon-message {
        color: #666;
        margin-bottom: 15px;
        font-size: 0.95rem;
    }
    
    /* Style the badge */
    .coming-soon-badge {
        background-color: #FF9800;
        color: white;
        font-size: 10px;
        padding: 3px 8px;
        border-radius: 10px;
        font-weight: bold;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Define supported languages with their ISO codes, names and flags
# This can be extended with more languages as needed
SUPPORTED_LANGUAGES = {
    "fin": {"name": "Finnish", "flag": "🇫🇮", "native_name": "Suomi"},
    "spa": {"name": "Spanish", "flag": "🇪🇸", "native_name": "Español"},
    "fra": {"name": "French", "flag": "🇫🇷", "native_name": "Français"},
    "deu": {"name": "German", "flag": "🇩🇪", "native_name": "Deutsch"},
    "ita": {"name": "Italian", "flag": "🇮🇹", "native_name": "Italiano"},
    "rus": {"name": "Russian", "flag": "🇷🇺", "native_name": "Русский"},
    "swe": {"name": "Swedish", "flag": "🇸🇪", "native_name": "Svenska"},
}

# Define common greetings for each language
LANGUAGE_GREETINGS = {
    "fin": {
        "morning": "Hyvää huomenta!",
        "afternoon": "Hyvää päivää!",
        "evening": "Hyvää iltaa!"
    },
    "spa": {
        "morning": "¡Buenos días!",
        "afternoon": "¡Buenas tardes!",
        "evening": "¡Buenas noches!"
    },
    "fra": {
        "morning": "Bonjour!",
        "afternoon": "Bon après-midi!",
        "evening": "Bonsoir!"
    },
    "deu": {
        "morning": "Guten Morgen!",
        "afternoon": "Guten Tag!",
        "evening": "Guten Abend!"
    },
    "ita": {
        "morning": "Buongiorno!",
        "afternoon": "Buon pomeriggio!",
        "evening": "Buonasera!"
    },
    "rus": {
        "morning": "Доброе утро!",
        "afternoon": "Добрый день!",
        "evening": "Добрый вечер!"
    },
    "swe": {
        "morning": "God morgon!",
        "afternoon": "God dag!",
        "evening": "God kväll!"
    }
}

# Define Finnish language levels with detailed descriptions
level_options = ["A1 (Beginner)", "A2 (Elementary)", "B1 (Intermediate)", "B2 (Upper Intermediate)", "C1 (Advanced)"]

level_descriptions = {
    "A1 (Beginner)": "Basic phrases and everyday expressions. Simple personal details.",
    "A2 (Elementary)": "Familiar expressions for basic routines. Simple communication about immediate needs.",
    "B1 (Intermediate)": "Main points on familiar matters. Simple connected text on familiar topics.",
    "B2 (Upper Intermediate)": "Understanding complex text. Spontaneous interaction with native speakers.",
    "C1 (Advanced)": "Understanding demanding, longer texts. Expressing ideas fluently and spontaneously."
}

# Define future features to showcase
future_features = [
    {
        "title": "🎙️ Speech Practice",
        "description": "Practice pronunciation with AI feedback and engage in spoken conversations",
        "coming_soon": False  # Implemented!
    },
    {
        "title": "📊 Progress Analytics",
        "description": "Track your learning journey with detailed stats and personalized recommendations",
        "coming_soon": True
    },
    {
        "title": "👥 Language Community",
        "description": "Connect with other learners and participate in language exchange sessions",
        "coming_soon": True
    },
    {
        "title": "📚 Content Library",
        "description": "Access curated reading materials categorized by language and level",
        "coming_soon": True
    },
    {
        "title": "📱 Mobile & Offline Mode",
        "description": "Learn on the go with our mobile app and download lessons for offline study",
        "coming_soon": True
    },
    {
        "title": "🌐 Immersive Learning",
        "description": "Experience language in context through virtual scenarios and simulations",
        "coming_soon": True
    }
]

# Define detailed descriptions for each feature
detailed_descriptions = {
    "🎙️ Speech Practice": "Our AI-powered speech recognition system will analyze your pronunciation and provide real-time feedback to help you sound more like a native speaker. You'll be able to practice conversations, receive personalized pronunciation tips, and track your improvement over time.",
    
    "📊 Progress Analytics": "Track your language learning journey with comprehensive analytics. See your vocabulary growth, grammar improvement, time spent practicing, and personalized recommendations for areas to focus on next. Set goals and monitor your progress with beautiful visualizations.",
    
    "👥 Language Community": "Connect with fellow language learners and native speakers through our community platform. Join language exchange sessions, participate in group challenges, get feedback on your writing, and make friends with people who share your interest in learning languages.",
    
    "📚 Content Library": "Access a vast library of level-appropriate reading materials, videos, podcasts, and exercises. All content is carefully curated and tagged by language level, topic, and grammar concepts to provide you with the perfect learning resources for your current proficiency.",
    
    "📱 Mobile & Offline Mode": "Take your language learning anywhere with our mobile app. Download lessons, exercises, and practice materials for offline use when you don't have internet access. Your progress will automatically sync when you reconnect.",
    
    "🌐 Immersive Learning": "Experience language in realistic contexts through interactive scenarios and simulations. Practice ordering food at a restaurant, asking for directions, or having a job interview in your target language with our AI-powered virtual environments."
}

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'chat_started' not in st.session_state:
    st.session_state.chat_started = False
if 'greeting_added' not in st.session_state:
    st.session_state.greeting_added = False
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'selected_level' not in st.session_state:
    st.session_state.selected_level = "B1 (Intermediate)"
if 'level_history' not in st.session_state:
    st.session_state.level_history = []  # Track level changes for adaptive learning
if 'user_topics' not in st.session_state:
    st.session_state.user_topics = []
if 'current_level_changed' not in st.session_state:
    st.session_state.current_level_changed = False
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "fin"  # Default to Finnish
if 'language_changed' not in st.session_state:
    st.session_state.language_changed = False

# Sidebar
with st.sidebar:
    st.markdown("<h1 class='sidebar-title'>🌍 AI Tutor</h1>", unsafe_allow_html=True)
    
    # Language selection
    st.markdown("### Select your target language")
    
    # Current language info
    current_lang_code = st.session_state.selected_language
    current_lang = SUPPORTED_LANGUAGES[current_lang_code]
    current_lang_flag = current_lang["flag"]
    current_lang_name = current_lang["name"]
    current_lang_native = current_lang["native_name"]
    
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <span class="language-flag" style="font-size: 1.5rem;">{current_lang_flag}</span>
        <span style="font-weight: bold;">{current_lang_name}</span> 
        <span style="font-style: italic;">({current_lang_native})</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create language selection options
    language_options = {}
    for code, lang_info in SUPPORTED_LANGUAGES.items():
        language_options[f"{lang_info['flag']} {lang_info['name']} ({lang_info['native_name']})"] = code
    
    # Language dropdown
    selected_language_display = st.selectbox(
        "Change language",
        options=list(language_options.keys()),
        index=list(language_options.keys()).index(f"{current_lang_flag} {current_lang_name} ({current_lang_native})"),
        key="language_selector"
    )
    
    # Update selected language if changed
    selected_language_code = language_options[selected_language_display]
    if selected_language_code != st.session_state.selected_language:
        st.session_state.selected_language = selected_language_code
        st.session_state.language_changed = True
        
        # Add a system message about the language change
        new_lang = SUPPORTED_LANGUAGES[selected_language_code]
        language_message = f"Your target language has been changed to {new_lang['flag']} {new_lang['name']}. All content will now be adapted to this language."
        st.session_state.messages.append({"role": "assistant", "content": language_message})
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": language_message, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        st.rerun()
    
    st.markdown("---")
    
    # Language level selection with detailed info
    st.markdown("### Select your proficiency level")
    
    # Extract current level code
    current_level_code = st.session_state.selected_level.split()[0]
    
    # Show current level with color-coded badge
    current_level_color = get_level_color(current_level_code)
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <span class="level-badge {current_level_code}" style="background-color: {current_level_color};">{current_level_code}</span>
        <span>{st.session_state.selected_level.split('(')[1].strip(')')}</span>
    </div>
    <div style="font-size: 0.9rem; font-style: italic; margin-bottom: 15px; padding: 10px;" class="level-bg-{current_level_code}">
        {level_descriptions.get(st.session_state.selected_level, "")}
    </div>
    """, unsafe_allow_html=True)
    
    selected_level = st.selectbox(
        "Change level",
        level_options,
        index=level_options.index(st.session_state.selected_level),
        key="level_selector",
        help="Choose your current language proficiency level"
    )
    
    if selected_level != st.session_state.selected_level:
        # Record the level change in history
        st.session_state.level_history.append({
            "from": st.session_state.selected_level,
            "to": selected_level,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "language": st.session_state.selected_language
        })
        
        # Update current level
        st.session_state.selected_level = selected_level
        st.session_state.current_level_changed = True
        
        # Add a system message about the level change
        lang_info = SUPPORTED_LANGUAGES[st.session_state.selected_language]
        level_message = f"Your {lang_info['name']} level has been changed to {selected_level}. All content will now be adapted to this level."
        st.session_state.messages.append({"role": "assistant", "content": level_message})
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": level_message, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        st.rerun()

    st.markdown("---")

    # AI Model selection
    st.markdown("### 🤖 AI Model Selection")

    # Initialize model selection in session state
    if 'model_provider' not in st.session_state:
        st.session_state.model_provider = "openai"
    if 'ollama_model' not in st.session_state:
        st.session_state.ollama_model = "qwen3:0.6b"

    # Model provider selection
    model_provider = st.selectbox(
        "Select AI Provider",
        options=["openai", "ollama"],
        index=0 if st.session_state.model_provider == "openai" else 1,
        help="OpenAI: GPT models (requires API key)\nOllama: Free local models (requires Ollama installed)"
    )

    st.session_state.model_provider = model_provider

    if model_provider == "ollama":
        st.markdown("**Ollama Configuration**")
        st.info("💡 Make sure Ollama is running: `ollama serve`")

        # Common small Ollama models
        ollama_models = {
            "qwen3:0.6b": " qwen3:0.6b - The Fastest",
            "phi3": "phi3 (3.8B) - Fast & capable",
            "gemma2:2b": "gemma2:2b (2B) - Very fast",
            "llama3.2:1b": "llama3.2:1b (1B) - Smallest",
            "qwen2.5:3b": "qwen2.5:3b (3B) - Efficient",
            "custom": "Custom model name..."
        }

        selected_ollama_display = st.selectbox(
            "Select Ollama Model",
            options=list(ollama_models.keys()),
            index=list(ollama_models.keys()).index(st.session_state.ollama_model) if st.session_state.ollama_model in ollama_models else 0,
            format_func=lambda x: ollama_models[x]
        )

        if selected_ollama_display == "custom":
            custom_model = st.text_input("Enter model name", value="llama3.2")
            st.session_state.ollama_model = custom_model
        else:
            st.session_state.ollama_model = selected_ollama_display

        # Display current model info
        st.caption(f"Using: {st.session_state.ollama_model}")
    else:
        st.caption("Using: OpenAI GPT")
        # Check if API key is configured
        if not st.secrets.get("OPENAI_API_KEY"):
            st.warning("⚠️ OpenAI API key not configured in .streamlit/secrets.toml")

    st.markdown("---")

    # File upload (now accepts any file type)
    st.markdown("### Upload File")
    current_lang_name = SUPPORTED_LANGUAGES[st.session_state.selected_language]["name"]
    uploaded_file = st.file_uploader(f"Upload a file with {current_lang_name} content", type=None)
    
    if uploaded_file is not None:
        # Display information about the uploaded file
        file_details = {
            "Filename": uploaded_file.name,
            "File type": uploaded_file.type or "Unknown",
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        
        st.write("### File Details:")
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")
        
        # Show preview for image files
        if uploaded_file.type and uploaded_file.type.startswith('image/'):
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        # Process the file if user clicks the button
        if st.button("Process File", key="process_file"):
            with st.spinner("Processing file..."):
                # Process the file using the utility function
                processed_file = process_uploaded_file(uploaded_file)
                st.session_state.uploaded_file = processed_file
                
                # Get level code for the message
                level_code = st.session_state.selected_level.split()[0]  # A1, A2, etc.
                level_badge = format_level_badge(level_code)
                
                # Get language info
                lang_info = SUPPORTED_LANGUAGES[st.session_state.selected_language]
                
                # Add a system message to inform the user that the file was uploaded
                system_msg = f"{level_badge} File '{uploaded_file.name}' has been uploaded. You can now ask questions about it, request translations of text in the file, or ask for exercises based on it that are adapted to your {level_code} level {lang_info['name']} learning."
                st.session_state.messages.append({"role": "assistant", "content": system_msg})
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": system_msg, 
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.rerun()
    
    st.markdown("---")
    
    # Session controls
    st.markdown("### Session Controls")
    
    if st.button("🔄 Reset Conversation", key="new_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.chat_started = False
        st.session_state.greeting_added = False
        st.session_state.uploaded_file = None
        st.session_state.user_topics = []
        # Keep the level history for learning progression tracking
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    if st.button("📝 Export Chat History", key="export_chat", use_container_width=True):
        # Generate markdown format
        markdown_text = get_chat_history_markdown(st.session_state)
        # Encode to download
        b64 = base64.b64encode(markdown_text.encode()).decode()
        lang_code = st.session_state.selected_language
        lang_name = SUPPORTED_LANGUAGES[lang_code]["name"].lower()
        file_name = f"ai_tutor_{lang_name}_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        href = f'<a href="data:text/markdown;base64,{b64}" download="{file_name}">Click to download chat history (Markdown)</a>'
        st.markdown(href, unsafe_allow_html=True)

    # Display level history
    if st.session_state.level_history:
        st.markdown("### Your Level Progress")
        level_history_md = ""
        for i, change in enumerate(st.session_state.level_history[-5:]):  # Show last 5 changes
            from_code = change["from"].split()[0]
            to_code = change["to"].split()[0]
            from_badge = format_level_badge(from_code)
            to_badge = format_level_badge(to_code)
            date = change["timestamp"].split()[0]
            language = change.get("language", "fin")  # Default to Finnish for backward compatibility
            language_flag = SUPPORTED_LANGUAGES[language]["flag"]
            level_history_md += f"{language_flag} {from_badge} → {to_badge} on {date}<br>"
        
        st.markdown(f"<div style='font-size: 0.9rem;'>{level_history_md}</div>", unsafe_allow_html=True)

# Main content
# Get level code and badge
level_code = st.session_state.selected_level.split()[0]
level_badge = format_level_badge(level_code)

# Get language info
lang_code = st.session_state.selected_language
lang_info = SUPPORTED_LANGUAGES[lang_code]
lang_flag = lang_info["flag"]
lang_name = lang_info["name"]

# Use markdown for title with HTML instead of st.title
st.markdown(f"""<div class="main-title">{lang_flag} AI {lang_name} Language Tutor {level_badge}</div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="welcome-card">
    <div class="welcome-header">
        <div class="welcome-icon">{lang_flag}</div>
        <h2>Welcome to AI Tutor</h2>
    </div>
    <div style="text-align: left; font-size: 15px; margin-top: 20px; line-height: 1.6;">
        <p>I'm your adaptive {lang_name} language tutor. I can help you with:</p>
        <ul style="list-style-position: inside; text-align: left; display: inline-block;">
            <li><strong>Translations</strong> - between {lang_name} and English (use format: "T: text")</li>
            <li><strong>Grammar explanations</strong> - including {lang_name}-specific grammar rules</li>
            <li><strong>Personalized exercises</strong> - reading, writing, vocabulary, and quizzes</li>
            <li><strong>Assignment help</strong> - upload your assignment in any file format</li>
            <li><strong>Content-based learning</strong> - upload files to learn from text, images, or documents</li>
        </ul>
        <div style="margin-top: 15px; padding: 15px; border-radius: 8px; border-left: 4px solid {get_level_color(level_code)};" class="level-bg-{level_code}">
            <p style="margin: 0; font-weight: bold;">
                {level_badge} You're currently learning {lang_name} at the {st.session_state.selected_level} level
            </p>
            <p style="margin-top: 8px; font-size: 0.9rem;">
                {level_descriptions.get(st.session_state.selected_level, "")}
            </p>
        </div>
        <p>Start by typing a message below, or upload a file from the sidebar.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Future features showcase with tabs
st.markdown("<h2 class='features-heading'>🔮 Future Features</h2>", unsafe_allow_html=True)
st.markdown("<p style='margin-bottom: 20px;'>Explore upcoming features that will enhance your language learning experience:</p>", unsafe_allow_html=True)

# Create tabs for each feature
feature_tabs = st.tabs([f"{feature['title']}" for feature in future_features])

# Fill each tab with content
for i, tab in enumerate(feature_tabs):
    with tab:
        feature = future_features[i]
        tab_title = feature["title"]

        # Check if feature is implemented or coming soon
        if feature.get("coming_soon", True):
            # Display "coming soon" message for unimplemented features
            st.markdown(f"""
            <div class="coming-soon-container">
                <div class="coming-soon-icon">⏳</div>
                <div class="coming-soon-title">{tab_title} <span class="coming-soon-badge">Coming Soon</span></div>
                <p class="coming-soon-message">{detailed_descriptions[tab_title]}</p>
                <p style="font-size: 0.9rem; color: #888;">We're working hard to bring this feature to you. Stay tuned for updates!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Render the implemented feature
            if tab_title == "🎙️ Speech Practice":
                render_speech_practice_tab(st.session_state)

# Add a divider after the feature tabs
st.markdown("<hr style='margin: 25px 0; opacity: 0.2;'>", unsafe_allow_html=True)

# Display chat messages with level indicators
if st.session_state.messages:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message['content'])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                # Insert level badge for system messages about level changes
                if "level has been changed" in message['content'] or "has been uploaded" in message['content'] or "language has been changed" in message['content']:
                    # Keep the level badge if it's already there
                    if not message['content'].startswith('<span class="level-badge'):
                        # Find which level this message was for
                        if i > 0 and "level has been changed to" in message['content']:
                            # Extract the level from the message
                            for level_option in level_options:
                                if level_option in message['content']:
                                    level = level_option.split()[0]
                                    message_with_badge = format_level_badge(level) + " " + message['content']
                                    st.markdown(message_with_badge, unsafe_allow_html=True)
                                    break
                            else:
                                st.markdown(message['content'], unsafe_allow_html=True)
                        else:
                            # Just use the current level
                            message_with_badge = format_level_badge(level_code) + " " + message['content']
                            st.markdown(message_with_badge, unsafe_allow_html=True)
                    else:
                        st.markdown(message['content'], unsafe_allow_html=True)
                else:
                    st.markdown(message['content'], unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Type your message here...")
if user_input:
    # Add greeting if it's the first message and hasn't been added yet
    if len(st.session_state.messages) == 0 and not st.session_state.greeting_added:
        # Add system greeting with introductory message
        now = datetime.now().hour
        
        # Get appropriate greeting based on time of day and language
        lang_code = st.session_state.selected_language
        greetings = LANGUAGE_GREETINGS.get(lang_code, LANGUAGE_GREETINGS["fin"])  # Default to Finnish if not found
        
        if now < 12:
            greeting = f"{greetings['morning']} (Good morning!) 🌞"
        elif now < 18:
            greeting = f"{greetings['afternoon']} (Good afternoon!) 🌤️"
        else:
            greeting = f"{greetings['evening']} (Good evening!) 🌙"
        
        # Format greeting with level badge and language info
        level_badge = format_level_badge(level_code)
        lang_info = SUPPORTED_LANGUAGES[lang_code]
        
        intro_message = f"{greeting} I'm your {lang_info['name']} language tutor. {level_badge} You've selected the {st.session_state.selected_level} level. I'll adapt all my responses, exercises, and vocabulary to this level. How can I help you today?"
        st.session_state.messages.append({"role": "assistant", "content": intro_message})
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": intro_message, 
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.session_state.greeting_added = True
    
    # Process the user's question
    process_question(user_input, st.session_state)
    st.rerun()

