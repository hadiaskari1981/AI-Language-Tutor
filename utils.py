import streamlit as st
import base64
import re
import mimetypes
import functools
from typing import Tuple

# Level-specific color scheme
def get_level_color(level_code):
    """
    Get the color associated with a specific CEFR level
    
    Parameters:
    - level_code: The language level code (A1, A2, etc.)
    
    Returns:
    - Hex color code
    """
    level_colors = {
        "A1": "#4CAF50",  # Green for beginner
        "A2": "#8BC34A",  # Light green for elementary
        "B1": "#2196F3",  # Blue for intermediate
        "B2": "#3F51B5",  # Indigo for upper intermediate
        "C1": "#9C27B0"   # Purple for advanced
    }
    return level_colors.get(level_code, "#0066FF")

# Function to create HTML level badge
def format_level_badge(level_code):
    """
    Create an HTML-formatted level badge
    
    Parameters:
    - level_code: The language level code (A1, A2, etc.)
    
    Returns:
    - HTML string for the formatted badge
    """
    color = get_level_color(level_code)
    return f'<span class="level-badge {level_code}" style="background-color: {color};">{level_code}</span>'

# Function to process uploaded files (any type)
def process_uploaded_file(uploaded_file):
    """
    Process an uploaded file of any type to prepare it for analysis by the LLM
    """
    if uploaded_file is None:
        return None
    
    # Read the file
    bytes_data = uploaded_file.getvalue()
    
    # Convert to base64 for displaying or sending to API
    base64_file = base64.b64encode(bytes_data).decode('utf-8')
    
    # Attempt to detect file type if not provided
    file_type = uploaded_file.type
    if not file_type:
        # Try to guess the MIME type based on filename
        guessed_type, _ = mimetypes.guess_type(uploaded_file.name)
        if guessed_type:
            file_type = guessed_type
        else:
            # Default to binary if can't determine
            file_type = "application/octet-stream"
    
    # Determine if file is text-based for potential direct content extraction
    is_text_file = file_type.startswith(('text/', 'application/json', 'application/xml'))
    
    # For text files, try to extract content
    text_content = None
    if is_text_file:
        try:
            text_content = bytes_data.decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try other common encodings
            try:
                text_content = bytes_data.decode('latin-1')
            except:
                # If still can't decode, leave as None
                pass
    
    # Include the current language level and language in the processed file data
    # This ensures both are available when processing the file
    current_level = st.session_state.selected_level
    level_code = current_level.split()[0]  # Extract just the level code (A1, A2, etc.)
    
    # Get current language
    language_code = st.session_state.selected_language if hasattr(st.session_state, 'selected_language') else "fin"
    
    return {
        "name": uploaded_file.name,
        "data": bytes_data,
        "base64": base64_file,
        "type": file_type,
        "is_text_file": is_text_file,
        "text_content": text_content,
        "language_level": current_level,
        "level_code": level_code,
        "language_code": language_code
    }

# Legacy function for backward compatibility
def process_uploaded_image(uploaded_file):
    """
    Legacy function that calls the more generic process_uploaded_file
    Kept for backward compatibility
    """
    return process_uploaded_file(uploaded_file)

# Function to format grammar tables with proper styling
def format_grammar_table(headers, rows, level_code=None):
    """
    Create an HTML table with proper styling for grammar explanations
    
    Parameters:
    - headers: List of column headers
    - rows: List of rows, where each row is a list of values
    - level_code: Optional level code to style the table appropriately
    
    Returns:
    - HTML string for the formatted table
    """
    # If level code is provided, use its color for the table header
    header_color = get_level_color(level_code) if level_code else "#0066FF"
    
    html = f'<table class="grammar-table" style="border-top: 3px solid {header_color};">'
    
    # Add headers
    html += f'<thead><tr style="background-color: {header_color};">'
    for header in headers:
        html += f'<th>{header}</th>'
    html += '</tr></thead>'
    
    # Add rows
    html += '<tbody>'
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody>'
    
    html += '</table>'
    return html

# Function to highlight important grammar points
def highlight_text(text, highlight_type="info", level_code=None):
    """
    Create a highlighted text box for important information
    
    Parameters:
    - text: The text to highlight
    - highlight_type: "info", "warning", or "success"
    - level_code: Optional level code to style the highlight appropriately
    
    Returns:
    - HTML string for the highlighted text
    """
    if level_code:
        # Use level-specific color if level code is provided
        level_color = get_level_color(level_code)
        colors = {
            "info": (f"rgba({','.join(str(int(c * 255)) for c in level_color.strip('#').lstrip('0')[::2])}, 0.1)", level_color),
            "warning": ("#fff3e6", "#ff9500"),
            "success": ("#e6fff0", "#00cc66")
        }
    else:
        colors = {
            "info": ("#e6f7ff", "#0066FF"),  # Light blue background, blue border
            "warning": ("#fff3e6", "#ff9500"),  # Light orange background, orange border
            "success": ("#e6fff0", "#00cc66")  # Light green background, green border
        }
    
    bg_color, border_color = colors.get(highlight_type, colors["info"])
    
    # Add level badge if level code is provided
    level_badge = format_level_badge(level_code) + " " if level_code else ""
    
    html = f"""
    <div style="background-color: {bg_color}; 
                border-left: 4px solid {border_color}; 
                padding: 10px; 
                border-radius: 4px; 
                margin: 10px 0;">
        {level_badge}{text}
    </div>
    """
    return html

# Function to format vocabulary lists in a visually appealing way
def format_vocabulary_list(vocab_pairs, level, language_name=None):
    """
    Create an HTML formatted vocabulary list with level-appropriate styling
    
    Parameters:
    - vocab_pairs: List of tuples (target_word, english_translation)
    - level: The language level (A1, A2, etc.) or full level string
    - language_name: Optional language name to display
    
    Returns:
    - HTML string for the formatted vocabulary list
    """
    # Extract level code if full level string is provided
    if "(" in level:
        level_code = level.split()[0]
    else:
        level_code = level
    
    # Set color based on level
    color = get_level_color(level_code)
    
    # Default to 'Vocabulary' if no language name is provided
    title = f"{language_name} Vocabulary List" if language_name else "Vocabulary List"
    
    html = f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-top: 3px solid {color};">'
    
    # Add level badge
    level_badge = format_level_badge(level_code)
    html += f'<h3 style="margin-top: 0; color: {color};">{level_badge} {title}</h3>'
    
    # Add level-specific note
    level_notes = {
        "A1": "Basic, high-frequency words for beginners",
        "A2": "Common everyday vocabulary",
        "B1": "More varied vocabulary for familiar topics",
        "B2": "Broader vocabulary including some specialized terms",
        "C1": "Advanced vocabulary including idiomatic expressions"
    }
    note = level_notes.get(level_code, "")
    if note:
        html += f'<p style="font-style: italic; margin-bottom: 15px;">{note}</p>'
    
    html += '<ul style="list-style-type: none; padding: 0;">'
    
    for target_word, english in vocab_pairs:
        html += f"""
        <li style="padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
            <strong>{target_word}</strong> - {english}
        </li>
        """
    
    html += '</ul></div>'
    return html

# Function to detect language of text using LLM with pattern-based fallback
def detect_language(text: str) -> str:
    """
    Detect the language of a text using LLM with regex-based fallback
    
    Parameters:
    - text: Text to analyze
    
    Returns:
    - Most likely language code (three-letter ISO code)
    """
    # If text is very short or empty, use traditional method
    if not text or len(text.strip()) < 10:
        return detect_language_traditional(text)
    
    # First try using LLM for detection (preferred method)
    try:
        detected_lang = detect_language_llm(text)
        # If detected language is in supported languages, return it
        import app
        if hasattr(app, 'SUPPORTED_LANGUAGES') and detected_lang in app.SUPPORTED_LANGUAGES:
            return detected_lang
    except Exception as e:
        import logging
        logging.warning(f"LLM language detection failed: {str(e)}. Falling back to traditional method.")
    
    # Fallback to traditional method if LLM fails or returns unsupported language
    return detect_language_traditional(text)

def detect_language_traditional(text: str) -> str:
    """
    Traditional language detection using character patterns
    (focused only on the supported languages)
    """
    if not text:
        return "eng"  # Default to English for empty text
        
    text_lower = text.lower()
    
    # Check for Finnish-specific characters
    if re.search(r'[äö]', text_lower) and re.search(r'\b(on|ei|ja|minä|sinä|hän|me|te|he)\b', text_lower):
        return "fin"
    
    # Check for Swedish-specific characters
    if re.search(r'[åäö]', text_lower) and re.search(r'\b(och|att|det|är|jag|du|han|hon|vi)\b', text_lower):
        return "swe"
    
    # Check for Spanish-specific characters/patterns
    if re.search(r'[áéíóúüñ¿¡]', text_lower) and re.search(r'\b(el|la|los|las|es|y|con|para|por)\b', text_lower):
        return "spa"
    
    # Check for French-specific characters/patterns
    if re.search(r'[àâçéèêëîïôùûüÿœæ]', text_lower) and re.search(r'\b(le|la|les|un|une|est|et|avec|dans)\b', text_lower):
        return "fra"
    
    # Check for German-specific characters
    if re.search(r'[äöüß]', text_lower) and re.search(r'\b(der|die|das|und|ist|ich|du|er|sie|wir)\b', text_lower):
        return "deu"
    
    # Check for Italian-specific patterns
    if re.search(r'[àèéìíîòóùú]', text_lower) and re.search(r'\b(il|lo|la|i|gli|le|e|sono|è|un|una)\b', text_lower):
        return "ita"
    
    # Check for Russian Cyrillic
    if re.search(r'[а-яА-Я]', text):
        return "rus"
    
    # Simpler checks for dominant character sets if the above failed
    if re.search(r'[äö]', text_lower):
        return "fin"  # Could be Finnish
    
    if re.search(r'[åäö]', text_lower):
        return "swe"  # Could be Swedish
        
    if re.search(r'[áéíóúüñ]', text_lower):
        return "spa"  # Could be Spanish
        
    if re.search(r'[àâçéèêëîïôùûüÿœæ]', text_lower):
        return "fra"  # Could be French
        
    if re.search(r'[äöüß]', text_lower):
        return "deu"  # Could be German
        
    if re.search(r'[àèéìíîòóùú]', text_lower):
        return "ita"  # Could be Italian
    
    # Default to English if no specific patterns are found
    return "eng"

def detect_language_traditional_with_confidence(text: str) -> Tuple[str, float]:
    """
    Traditional language detection with confidence score
    
    Returns:
    - Tuple of (language_code, confidence_score)
    """
    # Calculate pattern matches for each language
    lang_patterns = {
        "fin": r'[äöå]',
        "spa": r'[áéíóúüñ¿¡]',
        "fra": r'[àâçéèêëîïôùûüÿœæ]',
        "deu": r'[äöüß]',
        "rus": r'[а-яА-Я]',
        "jpn": r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]',
        "zho": r'[\u4e00-\u9fff]',
        "kor": r'[\uac00-\ud7a3]',
        "ara": r'[\u0600-\u06ff]'
    }
    
    best_match = {"lang": "eng", "confidence": 0.1}  # Default to English with low confidence
    
    # Calculate match density for each language
    for lang, pattern in lang_patterns.items():
        matches = re.findall(pattern, text.lower())
        if matches:
            # Calculate confidence based on match density
            density = len(matches) / len(text)
            confidence = min(0.95, density * 10)  # Scale and cap at 0.95
            
            # Special case for Chinese/Japanese to differentiate
            if lang == "zho" and re.search(r'[\u3040-\u30ff]', text):
                continue  # Skip this match if Japanese characters are present
                
            if confidence > best_match["confidence"]:
                best_match = {"lang": lang, "confidence": confidence}
    
    return best_match["lang"], best_match["confidence"]

# Use caching for LLM-based detection to improve performance
@functools.lru_cache(maxsize=100)
def detect_language_llm(text: str) -> str:
    """
    Detect language using LLM with caching
    """
    # Import required libraries
    from langchain_openai import ChatOpenAI
    import streamlit as st
    
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OpenAI API key not configured in Streamlit secrets")
    
    # Initialize the LLM
    model_name = st.secrets.get("MODEL_NAME", "gpt-4.1-mini-2025-04-14")
    chat = ChatOpenAI(
        openai_api_key=api_key,
        model=model_name,
        max_tokens=50  # Small context since we just need the language code
    )
    
    # Get supported languages
    supported_languages = {
        "fin": "Finnish",
        "spa": "Spanish", 
        "fra": "French",
        "deu": "German",
        "ita": "Italian",
        "rus": "Russian",
        "swe": "Swedish",
        "eng": "English"
    }
    
    # Try to update with actual supported languages from app
    try:
        import app
        if hasattr(app, 'SUPPORTED_LANGUAGES'):
            supported_languages = {code: info["name"] for code, info in app.SUPPORTED_LANGUAGES.items()}
            # Add English if not in the list
            supported_languages.setdefault("eng", "English")
    except ImportError:
        pass
    
    # Create a list of supported language codes and names
    language_options = "\n".join([f"- {code}: {name}" for code, name in supported_languages.items()])
    
    # Limit text length for the prompt (using just a sample to save tokens)
    sample_text = text[:150].replace("\n", " ")
    
    # Prepare the prompt
    prompt = [
        {
            "role": "system", 
            "content": f"""You are a language detection system for a language learning application.
            Identify the language of the provided text. Focus only on detecting the language.
            
            The application supports these languages:
            {language_options}
            
            Respond ONLY with the appropriate three-letter language code from the list. 
            Your entire response should be just the language code (fin, spa, fra, deu, ita, rus, swe, or eng).
            """
        },
        {
            "role": "user",
            "content": f"Detect the language: \"{sample_text}\""
        }
    ]
    
    # Get the response from the LLM
    response = chat.invoke(prompt)
    
    # Extract the language code and clean it
    language_code = response.content.strip().lower()
    
    # Extract just the language code if the model didn't follow instructions
    if ":" in language_code:
        language_code = language_code.split(":", 1)[1].strip()
    
    # Further cleaning to get just the 3-letter code
    code_match = re.search(r'\b([a-z]{3})\b', language_code)
    if code_match:
        language_code = code_match.group(1)
    else:
        # Default to English if no valid code found
        language_code = "eng"
    
    # Validate that it's a supported language
    if language_code not in supported_languages:
        language_code = "eng"
        
    return language_code

# Function to extract exercise-related parameters from user input
def extract_exercise_parameters(text):
    """
    Extract exercise type and other parameters from user request using LLM
    
    Parameters:
    - text: User's request text
    
    Returns:
    - Dictionary with detected parameters
    """
    # Initialize with default values
    params = {
        "exercise_type": None,
        "language_direction": None,
        "topic": None
    }
    
    # If text is too short, return empty params
    if not text or len(text.strip()) < 10:
        return params
    
    try:
        # Try to use LLM for parameter extraction
        return extract_exercise_parameters_llm(text)
    except Exception as e:
        # Fallback to rule-based if LLM fails
        import logging
        logging.warning(f"LLM parameter extraction failed: {str(e)}. Using rule-based method.")
        
        # Rule-based fallback (original implementation)
        # Detect exercise type
        if re.search(r'\b(reading|read)\b', text, re.IGNORECASE):
            params["exercise_type"] = "reading"
        elif re.search(r'\b(writing|write)\b', text, re.IGNORECASE):
            params["exercise_type"] = "writing"
        elif re.search(r'\b(vocabulary|vocab|words)\b', text, re.IGNORECASE):
            params["exercise_type"] = "vocabulary"
        elif re.search(r'\b(quiz|test|practice)\b', text, re.IGNORECASE):
            params["exercise_type"] = "quiz"
        
        # Detect language direction
        from_to_match = re.search(r'\b(from|to)\s+(\w+)\b', text, re.IGNORECASE)
        if from_to_match:
            direction = from_to_match.group(1).lower()
            language = from_to_match.group(2).lower()
            
            if direction == "to" and language == "english":
                params["language_direction"] = "target-to-english"
            elif direction == "from" and language == "english":
                params["language_direction"] = "english-to-target"
        
        # Extract potential topic
        topic_match = re.search(r'about\s+([a-zA-Z\s]+)', text, re.IGNORECASE)
        if topic_match:
            params["topic"] = topic_match.group(1).strip()
        
        return params

@functools.lru_cache(maxsize=100)
def extract_exercise_parameters_llm(text):
    """
    Extract exercise parameters using LLM with caching
    """
    # Import required libraries
    from langchain_openai import ChatOpenAI
    import json
    import streamlit as st
    
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OpenAI API key not configured in Streamlit secrets")
    
    # Initialize the LLM
    model_name = st.secrets.get("MODEL_NAME", "gpt-4.1-mini-2025-04-14")
    chat = ChatOpenAI(
        openai_api_key=api_key,
        model=model_name,
        max_tokens=200  # Small context for parameter extraction
    )
    
    # Get current language if available
    current_language = "unknown"
    try:
        if hasattr(st.session_state, 'selected_language'):
            language_code = st.session_state.selected_language
            import app
            if hasattr(app, 'SUPPORTED_LANGUAGES') and language_code in app.SUPPORTED_LANGUAGES:
                current_language = app.SUPPORTED_LANGUAGES[language_code]["name"]
    except:
        pass
    
    # Prepare the prompt
    prompt = [
        {
            "role": "system", 
            "content": f"""You are a parameter extraction system for a language learning application.
            Extract key parameters from the user's exercise request.
            
            The user is learning {current_language}.
            
            Extract these parameters:
            1. exercise_type: The type of exercise requested (reading, writing, vocabulary, quiz, or null if none specified)
            2. language_direction: Direction of translation if applicable (target-to-english, english-to-target, or null)
            3. topic: The topic or theme of the exercise if specified (e.g., "travel", "food", "work")
            
            Respond with a valid JSON object containing these parameters.
            Example: {{"exercise_type": "reading", "language_direction": null, "topic": "holidays"}}
            """
        },
        {
            "role": "user",
            "content": f"Extract exercise parameters from this request: \"{text}\""
        }
    ]
    
    # Get the response from the LLM
    response = chat.invoke(prompt)
    response_content = response.content.strip()
    
    # Try to parse the response as JSON
    try:
        # Extract JSON object if embedded in text
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if json_match:
            params = json.loads(json_match.group(0))
        else:
            # Try parsing the whole response
            params = json.loads(response_content)
        
        # Ensure it's a dictionary with the expected keys
        if not isinstance(params, dict):
            params = {}
        
        # Set default values for missing keys
        params.setdefault("exercise_type", None)
        params.setdefault("language_direction", None)
        params.setdefault("topic", None)
        
    except:
        # If parsing fails, use empty parameters
        params = {
            "exercise_type": None,
            "language_direction": None,
            "topic": None
        }
    
    return params

# Function to get language-specific grammar features
def get_language_grammar_features(lang_code):
    """
    Returns specific grammar features for a language
    
    Parameters:
    - lang_code: The language code (fin, spa, etc.)
    
    Returns:
    - Dictionary with grammar features
    """
    grammar_features = {
        "fin": {
            "cases": ["nominative", "genitive", "partitive", "inessive", "elative", "illative", 
                      "adessive", "ablative", "allative", "essive", "translative", "comitative", "instructive"],
            "verb_types": ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6"],
            "special_features": ["consonant gradation", "vowel harmony", "partitive objects"]
        },
        "spa": {
            "tenses": ["presente", "pretérito", "imperfecto", "futuro", "condicional", "perfecto", "pluscuamperfecto"],
            "moods": ["indicativo", "subjuntivo", "imperativo", "condicional"],
            "special_features": ["ser vs estar", "por vs para", "reflexive verbs"]
        },
        "fra": {
            "tenses": ["présent", "passé composé", "imparfait", "futur simple", "conditionnel"],
            "moods": ["indicatif", "subjonctif", "impératif", "conditionnel"],
            "special_features": ["gender agreement", "partitive articles", "negation"]
        },
        "deu": {
            "cases": ["nominativ", "akkusativ", "dativ", "genitiv"],
            "tenses": ["präsens", "präteritum", "perfekt", "futur I", "futur II"],
            "special_features": ["word order", "separable verbs", "modal verbs"]
        },
        "ita": {
            "tenses": ["presente", "passato prossimo", "imperfetto", "futuro semplice", "condizionale"],
            "moods": ["indicativo", "congiuntivo", "imperativo", "condizionale"],
            "special_features": ["gender and number agreement", "articles", "prepositions"]
        },
        "rus": {
            "cases": ["nominative", "genitive", "dative", "accusative", "instrumental", "prepositional"],
            "aspects": ["perfective", "imperfective"],
            "special_features": ["verbal aspects", "motion verbs", "hard/soft consonants"]
        },
        "swe": {
            "articles": ["definite", "indefinite"],
            "tenses": ["presens", "preteritum", "perfekt", "pluskvamperfekt", "futurum"],
            "special_features": ["en/ett gender system", "word order", "verb conjugation"]
        }
    }
    
    # Return language-specific features or empty dict if language not found
    return grammar_features.get(lang_code, {})
    
def get_language_grammar_features(lang_code):
    """
    Returns specific grammar features for a language
    
    Parameters:
    - lang_code: The language code (fin, spa, etc.)
    
    Returns:
    - Dictionary with grammar features
    """
    grammar_features = {
        "fin": {
            "cases": ["nominative", "genitive", "partitive", "inessive", "elative", "illative", 
                      "adessive", "ablative", "allative", "essive", "translative", "comitative", "instructive"],
            "verb_types": ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6"],
            "special_features": ["consonant gradation", "vowel harmony", "partitive objects"]
        },
        "spa": {
            "tenses": ["presente", "pretérito", "imperfecto", "futuro", "condicional", "perfecto", "pluscuamperfecto"],
            "moods": ["indicativo", "subjuntivo", "imperativo", "condicional"],
            "special_features": ["ser vs estar", "por vs para", "reflexive verbs"]
        },
        "fra": {
            "tenses": ["présent", "passé composé", "imparfait", "futur simple", "conditionnel"],
            "moods": ["indicatif", "subjonctif", "impératif", "conditionnel"],
            "special_features": ["gender agreement", "partitive articles", "negation"]
        },
        "deu": {
            "cases": ["nominativ", "akkusativ", "dativ", "genitiv"],
            "tenses": ["präsens", "präteritum", "perfekt", "futur I", "futur II"],
            "special_features": ["word order", "separable verbs", "modal verbs"]
        },
        "ita": {
            "tenses": ["presente", "passato prossimo", "imperfetto", "futuro semplice", "condizionale"],
            "moods": ["indicativo", "congiuntivo", "imperativo", "condizionale"],
            "special_features": ["gender and number agreement", "articles", "prepositions"]
        },
        "rus": {
            "cases": ["nominative", "genitive", "dative", "accusative", "instrumental", "prepositional"],
            "aspects": ["perfective", "imperfective"],
            "special_features": ["verbal aspects", "motion verbs", "hard/soft consonants"]
        },
        "swe": {
            "articles": ["definite", "indefinite"],
            "tenses": ["presens", "preteritum", "perfekt", "pluskvamperfekt", "futurum"],
            "special_features": ["en/ett gender system", "word order", "verb conjugation"]
        }
    }
    
    # Return language-specific features or empty dict if language not found
    return grammar_features.get(lang_code, {})

# Function to get level-appropriate content for a specific language
def get_level_appropriate_content(level_code, language_code="fin"):
    """
    Get vocabulary and grammar structures appropriate for each CEFR level and language
    
    Parameters:
    - level_code: The language level code (A1, A2, etc.)
    - language_code: The language code (fin, spa, etc.)
    
    Returns:
    - Dictionary with level-appropriate content guidelines
    """
    # Base content that's relatively language-agnostic
    base_content = {
        "A1": {
            "grammar": [
                "Basic present tense",
                "Simple questions",
                "Basic negation",
                "Personal pronouns",
                "Numbers 1-100",
                "Basic prepositions"
            ],
            "vocabulary": [
                "Basic greetings and introductions",
                "Family members",
                "Numbers and time expressions",
                "Food and drinks",
                "Basic everyday items",
                "Simple adjectives (good, bad, big, small)",
                "Basic verbs (to be, to have, to go, to come)"
            ],
            "example_sentences": [
                "My name is...",
                "I have a...",
                "She/he goes to...",
                "What are you doing?"
            ]
        },
        "A2": {
            "grammar": [
                "Past tense (simple)",
                "More question forms",
                "Possessives",
                "Plural forms",
                "Comparative forms",
                "More prepositions"
            ],
            "vocabulary": [
                "Weather and seasons",
                "Clothing",
                "Parts of the body",
                "Hobbies and free time",
                "Traveling and transportation",
                "Shopping and services",
                "House and home"
            ],
            "example_sentences": [
                "I went to the store yesterday.",
                "When did you arrive?",
                "My house is bigger than yours.",
                "In summer we go to the beach."
            ]
        },
        "B1": {
            "grammar": [
                "Perfect tenses",
                "Future tense",
                "Conditional forms",
                "Passive voice (simple)",
                "More complex sentence structures",
                "Relative clauses"
            ],
            "vocabulary": [
                "Work and professional life",
                "Education and studies",
                "Media and current events",
                "Health and wellbeing",
                "Nature and environment",
                "Emotions and feelings",
                "Abstract concepts"
            ],
            "example_sentences": [
                "If I had more time, I would study more.",
                "Have you already visited the new museum?",
                "This book was written by a famous author.",
                "Could you explain this again?"
            ]
        },
        "B2": {
            "grammar": [
                "All tenses",
                "Complex verbal constructions",
                "Reported speech",
                "Advanced conditional forms",
                "Expressing hypothesis",
                "Complex modifiers"
            ],
            "vocabulary": [
                "Political and social issues",
                "Science and technology",
                "Economics and business",
                "Arts and culture",
                "Idiomatic expressions",
                "Academic vocabulary",
                "Specialized terminology"
            ],
            "example_sentences": [
                "Experts claim that climate change significantly affects our planet.",
                "Without your help, I wouldn't have been able to solve this problem.",
                "If only I had studied harder!",
                "The matter will be announced later."
            ]
        },
        "C1": {
            "grammar": [
                "All grammatical structures",
                "Complex constructions",
                "Nuanced tense and mood usage",
                "Literary and formal structures",
                "Sophisticated syntax",
                "Dialectal variations"
            ],
            "vocabulary": [
                "Specialized professional terminology",
                "Literary and poetic language",
                "Colloquial and dialectal expressions",
                "Cultural references",
                "Humor and wordplay",
                "Philosophical concepts",
                "Very specific domain knowledge"
            ],
            "example_sentences": [
                "Had the government approved the bill, we would have had to change our entire operating model.",
                "The questions that emerged in the research will be addressed in more detail in future publications.",
                "His/her works reflect the transition period of society in the post-war era.",
                "Having said that, I realized I had made a mistake."
            ]
        }
    }
    
    # Language-specific content
    language_specific = {
        "fin": {
            "A1": {
                "grammar": [
                    "Basic present tense verb conjugation",
                    "Simple noun cases: nominative, partitive, genitive",
                    "Personal pronouns",
                    "Simple questions with question words",
                    "Basic negative sentences",
                    "Numbers 1-100",
                    "Simple consonant gradation (kk-k, pp-p, tt-t)"
                ],
                "vocabulary": [
                    "Basic greetings and introductions",
                    "Family members",
                    "Numbers and time expressions",
                    "Food and drinks",
                    "Basic everyday items",
                    "Simple adjectives (hyvä, paha, iso, pieni)",
                    "Basic verbs (olla, olla jollakin, mennä, tulla)"
                ],
                "example_sentences": [
                    "Minä olen Anna. (I am Anna.)",
                    "Minulla on koira. (I have a dog.)",
                    "Hän menee kauppaan. (He/she goes to the store.)",
                    "Mitä sinä teet? (What are you doing?)"
                ]
            },
            "A2": {
                "grammar": [
                    "All verb types in present tense",
                    "Past tense (imperfect)",
                    "Consonant gradation (more patterns)",
                    "Locative cases (inessive, elative, illative)",
                    "More question forms",
                    "Possessive suffixes (basic use)",
                    "Plural forms of nouns"
                ],
                "vocabulary": [
                    "Weather and seasons",
                    "Clothing",
                    "Parts of the body",
                    "Hobbies and free time",
                    "Traveling and transportation",
                    "Shopping and services",
                    "House and home"
                ],
                "example_sentences": [
                    "Minä kävin eilen kaupassa. (I went to the store yesterday.)",
                    "Milloin sinä tulit Suomeen? (When did you come to Finland?)",
                    "Minun autoni on sininen. (My car is blue.)",
                    "Kesällä me menemme mökille. (In summer we go to the cottage.)"
                ]
            },
            "B1": {
                "grammar": [
                    "Perfect and pluperfect tenses",
                    "Conditional mood",
                    "All case forms in singular and plural",
                    "More complex sentence structures",
                    "Passive voice in present and past",
                    "Relative pronouns (joka, mikä)"
                ],
                "vocabulary": [
                    "Work and employment",
                    "Education and learning",
                    "Health and wellbeing",
                    "Nature and environment",
                    "Emotions and feelings",
                    "Technology and media",
                    "Abstract concepts"
                ],
                "example_sentences": [
                    "Oletko käynyt Helsingissä aikaisemmin? (Have you been to Helsinki before?)",
                    "Jos minulla olisi enemmän aikaa, opiskelisin suomea enemmän. (If I had more time, I would study Finnish more.)",
                    "Kirja, jonka luin viime viikolla, oli todella kiinnostava. (The book that I read last week was really interesting.)",
                    "Talo on rakennettu 1950-luvulla. (The house was built in the 1950s.)"
                ]
            }
        },
        "spa": {
            "A1": {
                "grammar": [
                    "Present tense of regular -ar, -er, -ir verbs",
                    "Present tense of common irregular verbs (ser, estar, ir, tener)",
                    "Gender and number agreement",
                    "Definite and indefinite articles",
                    "Basic prepositions",
                    "Subject pronouns",
                    "Basic question words"
                ],
                "vocabulary": [
                    "Greetings and farewells",
                    "Family and relationships",
                    "Numbers and time",
                    "Food and restaurants",
                    "Daily activities",
                    "Basic adjectives",
                    "Countries and nationalities"
                ],
                "example_sentences": [
                    "Me llamo Juan. (My name is Juan.)",
                    "¿De dónde eres? (Where are you from?)",
                    "Tengo dos hermanos. (I have two siblings.)",
                    "Me gusta el café. (I like coffee.)"
                ]
            },
            "A2": {
                "grammar": [
                    "Preterite tense of regular verbs",
                    "Preterite of common irregular verbs",
                    "Imperfect tense",
                    "Reflexive verbs",
                    "Direct and indirect object pronouns",
                    "Comparatives and superlatives",
                    "Simple commands (tú form)"
                ],
                "vocabulary": [
                    "Shopping and clothing",
                    "Travel and transportation",
                    "House and furniture",
                    "Daily routines",
                    "Weather and seasons",
                    "Health and body parts",
                    "City and directions"
                ],
                "example_sentences": [
                    "Ayer fui al cine. (Yesterday I went to the movies.)",
                    "Cuando era niño, jugaba al fútbol. (When I was a child, I used to play soccer.)",
                    "Me duele la cabeza. (My head hurts.)",
                    "¿Cómo llego al museo? (How do I get to the museum?)"
                ]
            },
            "B1": {
                "grammar": [
                    "Present subjunctive",
                    "Future tense",
                    "Conditional tense",
                    "Perfect tenses (present perfect, pluperfect)",
                    "Por vs. para",
                    "Relative pronouns",
                    "Formal commands"
                ],
                "vocabulary": [
                    "Work and professions",
                    "Education and studies",
                    "Environment and nature",
                    "Technology and media",
                    "Culture and traditions",
                    "Emotions and opinions",
                    "Current events"
                ],
                "example_sentences": [
                    "Espero que puedas venir a la fiesta. (I hope you can come to the party.)",
                    "Cuando termine mis estudios, viajaré por Europa. (When I finish my studies, I will travel around Europe.)",
                    "Si tuviera más tiempo, aprendería a tocar el piano. (If I had more time, I would learn to play the piano.)",
                    "La película que vimos anoche fue muy interesante. (The movie we watched last night was very interesting.)"
                ]
            }
        },
        "fra": {
            "A1": {
                "grammar": [
                    "Present tense of regular -er verbs",
                    "Present tense of common irregular verbs (être, avoir, aller, faire)",
                    "Definite and indefinite articles",
                    "Gender and number of nouns",
                    "Basic adjectives (agreement and placement)",
                    "Basic prepositions",
                    "Question formation with est-ce que"
                ],
                "vocabulary": [
                    "Greetings and introductions",
                    "Numbers and time",
                    "Family members",
                    "Food and drinks",
                    "Daily activities",
                    "Basic descriptive adjectives",
                    "Countries and nationalities"
                ],
                "example_sentences": [
                    "Je m'appelle Marie. (My name is Marie.)",
                    "J'habite à Paris. (I live in Paris.)",
                    "Quelle heure est-il? (What time is it?)",
                    "J'aime le café. (I like coffee.)"
                ]
            },
            "A2": {
                "grammar": [
                    "Passé composé with avoir and être",
                    "Imparfait (introduction)",
                    "Reflexive verbs",
                    "Direct and indirect object pronouns",
                    "Comparative and superlative forms",
                    "Near future (aller + infinitive)",
                    "Imperative mood"
                ],
                "vocabulary": [
                    "Shopping and clothing",
                    "Travel and transportation",
                    "House and furniture",
                    "Weather and seasons",
                    "Health and body parts",
                    "Leisure activities",
                    "City and directions"
                ],
                "example_sentences": [
                    "J'ai visité Paris l'année dernière. (I visited Paris last year.)",
                    "Quand j'étais petit, j'aimais les bonbons. (When I was little, I liked candy.)",
                    "Je vais aller au cinéma ce soir. (I'm going to go to the movies tonight.)",
                    "Donnez-moi un café, s'il vous plaît. (Give me a coffee, please.)"
                ]
            },
            "B1": {
                "grammar": [
                    "All past tenses (passé composé, imparfait, plus-que-parfait)",
                    "Future simple",
                    "Conditional mood",
                    "Subjunctive mood (introduction)",
                    "Relative pronouns (qui, que, où, dont)",
                    "Passive voice",
                    "Reported speech"
                ],
                "vocabulary": [
                    "Work and employment",
                    "Education and studies",
                    "Environment and nature",
                    "Media and technology",
                    "Social issues",
                    "Emotions and opinions",
                    "Arts and culture"
                ],
                "example_sentences": [
                    "Si j'avais plus de temps, j'étudierais plus. (If I had more time, I would study more.)",
                    "Je veux que tu viennes à la fête. (I want you to come to the party.)",
                    "Le livre que j'ai lu était très intéressant. (The book I read was very interesting.)",
                    "Cette maison a été construite au 19ème siècle. (This house was built in the 19th century.)"
                ]
            }
        },
        "deu": {
            "A1": {
                "grammar": [
                    "Present tense of regular and common irregular verbs",
                    "Articles (definite and indefinite)",
                    "Nominative and accusative cases",
                    "Negation with nicht and kein",
                    "Basic question words",
                    "Possessive articles",
                    "Modal verbs (können, müssen, wollen)"
                ],
                "vocabulary": [
                    "Greetings and introductions",
                    "Numbers and time",
                    "Family members",
                    "Food and drinks",
                    "Daily activities",
                    "Basic adjectives",
                    "Countries and languages"
                ],
                "example_sentences": [
                    "Ich heiße Thomas. (My name is Thomas.)",
                    "Woher kommst du? (Where do you come from?)",
                    "Ich habe einen Bruder. (I have a brother.)",
                    "Können Sie mir helfen? (Can you help me?)"
                ]
            },
            "A2": {
                "grammar": [
                    "Perfect tense",
                    "Imperative forms",
                    "Dative case",
                    "Prepositions with accusative and dative",
                    "Comparative and superlative forms",
                    "Subordinate clauses with weil, dass, wenn",
                    "Reflexive verbs"
                ],
                "vocabulary": [
                    "Housing and furniture",
                    "Shopping and clothing",
                    "Travel and transportation",
                    "Weather and seasons",
                    "Health and body parts",
                    "Leisure activities",
                    "Work and professions"
                ],
                "example_sentences": [
                    "Ich habe gestern einen Film gesehen. (I watched a movie yesterday.)",
                    "Geben Sie mir bitte eine Tasse Kaffee. (Please give me a cup of coffee.)",
                    "Das Buch ist interessanter als der Film. (The book is more interesting than the movie.)",
                    "Ich weiß, dass er morgen kommt. (I know that he's coming tomorrow.)"
                ]
            },
            "B1": {
                "grammar": [
                    "Passive voice",
                    "Subjunctive II (Konjunktiv II)",
                    "Genitive case",
                    "Future tense",
                    "Relative clauses",
                    "Adjective endings",
                    "Conjunctions and linking words"
                ],
                "vocabulary": [
                    "Education and studies",
                    "Work and career",
                    "Media and technology",
                    "Environment and nature",
                    "Politics and society",
                    "Arts and culture",
                    "Emotions and opinions"
                ],
                "example_sentences": [
                    "Das Haus wurde im 19. Jahrhundert gebaut. (The house was built in the 19th century.)",
                    "Wenn ich Zeit hätte, würde ich mehr lesen. (If I had time, I would read more.)",
                    "Die Frau, deren Auto gestohlen wurde, ist sehr traurig. (The woman whose car was stolen is very sad.)",
                    "Nächstes Jahr werde ich nach Deutschland reisen. (Next year I will travel to Germany.)"
                ]
            }
        },
        "ita": {
            "A1": {
                "grammar": [
                    "Present tense of regular -are, -ere, -ire verbs",
                    "Present tense of common irregular verbs (essere, avere, fare, andare)",
                    "Definite and indefinite articles",
                    "Gender and number agreement",
                    "Basic prepositions",
                    "Basic question words",
                    "Simple adjectives (agreement and placement)"
                ],
                "vocabulary": [
                    "Greetings and introductions",
                    "Numbers and time",
                    "Family and relationships",
                    "Food and drinks",
                    "Daily activities",
                    "Basic descriptive adjectives",
                    "Countries and nationalities"
                ],
                "example_sentences": [
                    "Mi chiamo Marco. (My name is Marco.)",
                    "Di dove sei? (Where are you from?)",
                    "Ho due fratelli. (I have two brothers.)",
                    "Mi piace il caffè. (I like coffee.)"
                ]
            },
            "A2": {
                "grammar": [
                    "Passato prossimo with avere and essere",
                    "Imperfetto",
                    "Reflexive verbs",
                    "Direct and indirect object pronouns",
                    "Comparative and superlative forms",
                    "Future tense (introduction)",
                    "Imperative forms"
                ],
                "vocabulary": [
                    "Shopping and clothing",
                    "Travel and accommodations",
                    "House and furniture",
                    "Weather and seasons",
                    "Health and body parts",
                    "Leisure activities",
                    "City and directions"
                ],
                "example_sentences": [
                    "Ho visitato Roma l'anno scorso. (I visited Rome last year.)",
                    "Quando ero piccolo, giocavo a calcio. (When I was little, I used to play soccer.)",
                    "Mi sono svegliato alle sette. (I woke up at seven.)",
                    "Dammi un caffè, per favore. (Give me a coffee, please.)"
                ]
            },
            "B1": {
                "grammar": [
                    "Conditional tense",
                    "Congiuntivo presente",
                    "Passato remoto (recognition)",
                    "Future perfect",
                    "Relative pronouns (che, cui, quale)",
                    "Combined pronouns",
                    "Passive voice"
                ],
                "vocabulary": [
                    "Work and career",
                    "Education and studies",
                    "Environment and nature",
                    "Media and technology",
                    "Politics and society",
                    "Arts and culture",
                    "Emotions and opinions"
                ],
                "example_sentences": [
                    "Se avessi tempo, studierei di più. (If I had time, I would study more.)",
                    "Penso che tu abbia ragione. (I think you're right.)",
                    "Il libro che ho letto era molto interessante. (The book I read was very interesting.)",
                    "Questo edificio fu costruito nel diciottesimo secolo. (This building was built in the 18th century.)"
                ]
            }
        },
        "rus": {
            "A1": {
                "grammar": [
                    "Cyrillic alphabet and pronunciation",
                    "Personal pronouns",
                    "Present tense of common verbs",
                    "Nominative case",
                    "Simple questions",
                    "Gender of nouns",
                    "Numbers 1-100"
                ],
                "vocabulary": [
                    "Greetings and introductions",
                    "Family members",
                    "Basic food and drinks",
                    "Days of the week and months",
                    "Countries and nationalities",
                    "Simple everyday items",
                    "Basic adjectives"
                ],
                "example_sentences": [
                    "Меня зовут Иван. (My name is Ivan.)",
                    "Я живу в Москве. (I live in Moscow.)",
                    "Это моя книга. (This is my book.)",
                    "Ты говоришь по-русски? (Do you speak Russian?)"
                ]
            },
            "A2": {
                "grammar": [
                    "Past tense",
                    "Future tense",
                    "Accusative case",
                    "Prepositional case",
                    "Dative case (introduction)",
                    "Aspects of verbs (introduction)",
                    "Possessive pronouns"
                ],
                "vocabulary": [
                    "Housing and furniture",
                    "Shopping and clothing",
                    "Transportation",
                    "Weather and seasons",
                    "Health and body parts",
                    "Leisure activities",
                    "Food and restaurants"
                ],
                "example_sentences": [
                    "Вчера я был в кино. (Yesterday I was at the cinema.)",
                    "Я буду учить русский язык. (I will study the Russian language.)",
                    "Я живу в новой квартире. (I live in a new apartment.)",
                    "Дайте мне, пожалуйста, чашку кофе. (Please give me a cup of coffee.)"
                ]
            },
            "B1": {
                "grammar": [
                    "All cases (nominative, accusative, genitive, dative, instrumental, prepositional)",
                    "Aspects of verbs (perfective and imperfective)",
                    "Verbs of motion with prefixes",
                    "Conditional mood",
                    "Imperatives",
                    "Short form adjectives",
                    "Complex sentences with conjunctions"
                ],
                "vocabulary": [
                    "Work and career",
                    "Education and studies",
                    "Media and technology",
                    "Environment and nature",
                    "Politics and society",
                    "Arts and culture",
                    "Emotions and feelings"
                ],
                "example_sentences": [
                    "Если бы у меня было больше времени, я бы выучил русский язык. (If I had more time, I would learn Russian.)",
                    "Книга, которую я прочитал, была очень интересной. (The book I read was very interesting.)",
                    "Я приехал в Россию, чтобы изучать русскую литературу. (I came to Russia to study Russian literature.)",
                    "Этот дом был построен в девятнадцатом веке. (This house was built in the 19th century.)"
                ]
            }
        },
        "swe": {
            "A1": {
                "grammar": [
                    "Present tense of regular verbs",
                    "Common irregular verbs (är, har, gör)",
                    "Indefinite and definite forms of nouns",
                    "En and ett gender system",
                    "Personal pronouns",
                    "Basic word order",
                    "Numbers and time expressions"
                ],
                "vocabulary": [
                    "Greetings and introductions",
                    "Family members",
                    "Basic food and drinks",
                    "Days of the week and months",
                    "Countries and nationalities",
                    "Simple everyday items",
                    "Basic adjectives"
                ],
                "example_sentences": [
                    "Jag heter Erik. (My name is Erik.)",
                    "Jag kommer från Sverige. (I come from Sweden.)",
                    "Det är en bok. (It is a book.)",
                    "Talar du svenska? (Do you speak Swedish?)"
                ]
            },
            "A2": {
                "grammar": [
                    "Past tense (preteritum)",
                    "Perfect tense (perfekt)",
                    "Adjective agreement",
                    "Adverbs and word order",
                    "Modal verbs (kan, vill, måste)",
                    "Possessive pronouns",
                    "Comparative and superlative forms"
                ],
                "vocabulary": [
                    "Housing and furniture",
                    "Shopping and clothing",
                    "Travel and transportation",
                    "Weather and seasons",
                    "Health and body parts",
                    "Leisure activities",
                    "Work and occupations"
                ],
                "example_sentences": [
                    "Jag köpte en ny bil igår. (I bought a new car yesterday.)",
                    "Har du varit i Stockholm? (Have you been to Stockholm?)",
                    "Den röda bilen är min. (The red car is mine.)",
                    "Jag måste gå nu. (I must go now.)"
                ]
            },
            "B1": {
                "grammar": [
                    "Future constructions",
                    "Conditional forms (skulle)",
                    "Relative clauses",
                    "Passive voice",
                    "Subjunctive (in fixed expressions)",
                    "Subordinate clauses",
                    "Particles and phrasal verbs"
                ],
                "vocabulary": [
                    "Education and studies",
                    "Work and career",
                    "Media and technology",
                    "Environment and nature",
                    "Politics and society",
                    "Arts and culture",
                    "Emotions and opinions"
                ],
                "example_sentences": [
                    "Om jag hade mer tid, skulle jag läsa mer. (If I had more time, I would read more.)",
                    "Boken som jag läste var mycket intressant. (The book I read was very interesting.)",
                    "Huset byggdes på artonhundratalet. (The house was built in the 19th century.)",
                    "Jag kommer att resa till Sverige nästa år. (I will travel to Sweden next year.)"
                ]
            }
        }
    }
    
    # Start with base content for the level
    content = base_content.get(level_code, {})
    
    # If we have language-specific content for this level, override with it
    if language_code in language_specific and level_code in language_specific[language_code]:
        for key, value in language_specific[language_code][level_code].items():
            content[key] = value
    
    return content
