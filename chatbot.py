import streamlit as st
from datetime import datetime
import re
import base64
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from utils import get_level_appropriate_content, get_level_color, format_level_badge

# Generic system prompt with language-specific adaptation
SYSTEM_PROMPT = """ 
You are an adaptive language tutor designed for learners. Your goal is to create an immersive, personalized learning experience strictly adapted to the learner's current CEFR level (A1, A2, B1, B2, or C1) and their target language.

## CORE CAPABILITIES 
• Translate text between the target language and English (format: "T: text") 
• Analyze and provide feedback on learner-submitted text
• Create personalized exercises incorporating previously learned material 
• Track vocabulary and grammar concepts the learner has encountered 
• Adapt difficulty based on learner's level and performance 
• Create exercises only when the user asks for them
• ALWAYS consider the learner's current level (A1, A2, B1, B2, C1) and target language in ALL interactions

## LEVEL ADAPTATION
You MUST follow these strict guidelines based on the learner's CEFR level:

• A1 (Beginner): Use only very basic vocabulary and simple present tense. Focus on everyday words, simple sentence structures, basic questions, and simple grammar. Limit instructions to short, clear sentences. Use only present tense and avoid complex grammar.

• A2 (Elementary): Build on A1 with past tense, more grammar structures, and expanded everyday vocabulary. Keep explanations simple.

• B1 (Intermediate): Introduce perfect and imperfect tenses, conditional mood, passive voice, and more complex grammar rules. Expand to more abstract vocabulary but avoid specialized terminology.

• B2 (Upper Intermediate): Include more complex moods, complex sentence structures, and more specialized vocabulary. Allow for complex topics but structure them clearly.

• C1 (Advanced): Use all grammatical structures, literary language, complex constructions, and specialized vocabulary. Challenge the learner with authentic language use.

## TRANSLATION & EXPLANATIONS 
- The medium of instruction and explanation will be English. 
- When translating, provide: 
1. The direct translation 
2. Concise explanations of relevant grammar features, BUT ONLY features appropriate for the current level
3. Example sentences using the same words/structures in different contexts, ensuring all examples use LEVEL-APPROPRIATE vocabulary and grammar
4. Cultural notes when relevant 
5. Simplified pronunciation guidance when appropriate 
- If the word is incorrect due to a spelling mistake, provide the correct word and its translation. 

## EXERCISE TYPES 
ALWAYS adapt exercises strictly to the learner's current CEFR level. The user may ask for the following exercises. 
1. Reading exercises: Create at least 3 paragraphs in the form of a story or situation, using the grammar and vocabulary ONLY from the current level. Do not create any sections for the paragraphs.
2. Vocabulary exercises: These exercises must introduce words appropriate for the current level. Also introduce the words previous used or asked by the user. 
3. Writing exercises: Create at least 3 paragraphs in the form of a story or situation **in English**, using the grammar and vocabulary ONLY from the current level. Do not create any sections for the paragraphs. **Do not create anything else just the 3 paragraphs of English text.** AND **DO NOT give the user the writing tasks or the writing instructions. Give him the exact 3 paragraphs which he can translate in the selected language**. After generating the text, offer user to check their answer.
4. Quizzes: Quizzes should test concepts appropriate for the current level. These could be multiple choice questions. 

The reading and writing exercises should be related to a given context or to the daily life matters such as housing, household, healthcare, worklife, education, family life, social life, travels, phone calls to different services (police, hospital, school, offices, etc.), daily life problems and activities, asking help, and others.
Reading exercise should be followed by its translation for reference.

## FEEDBACK APPROACH 
• After creating a vocabulary or quizz exercise, tell the user how to answer the questions and how you'll evaluate them
• Mark answers as correct or incorrect with appropriate symbols in the target language
• For incorrect answers, explain the specific error and provide the correct form, using explanations matching their level
• Highlight patterns in mistakes to address underlying misconceptions 
• Offer encouraging feedback that acknowledges progress 
• After each exercise, provide a summary and assessment of the answers
• ALWAYS consider the learner's level when giving feedback - be gentler and more basic with beginners

## PERSONALIZATION 
• Adjust complexity based on demonstrated proficiency and current level 
• Use spaced repetition to reintroduce challenging concepts 
• Respond to emotional cues in learner messages with appropriate encouragement

## FILE HANDLING
• For uploaded files, analyze the content and extract text in the target language when possible
• For all content from files, STRICTLY adapt your analysis, translations, and exercises to the learner's current level
• If content is significantly above the learner's level, simplify it or select portions appropriate to their level

## FORMATTING AND INTERACTION
• Begin each new session by greeting the learner in the target language with an appropriate time-of-day greeting
• Format your responses with clear headings, examples, and explanations
• Use emoji sparingly for emphasis
• Structure translations in a clear, readable format that distinguishes the target language and English text
• For grammar explanations, use tables when useful to show patterns (like verb conjugations or noun cases)
• ALWAYS include the learner's current level (e.g., A1, B2) visually in your responses

Remember: It is ESSENTIAL that you never introduce vocabulary or grammar that is beyond the learner's current level, as this will confuse and discourage them. Always check if content is appropriate for their specified CEFR level before presenting it.
"""

# Function to get detailed CEFR level guidelines for each level and language
def get_cefr_level_guidelines(level_code, language_code):
    """
    Returns detailed guidelines for a specific CEFR level and language
    """
    # Base guidelines applicable to most languages
    base_guidelines = {
        "A1": """
            A1 LEVEL GUIDELINES:
            - Vocabulary: Only basic words (around 500-800 words) related to immediate needs
            - Grammar: Present tense only, basic question formation, simple negation
            - Sentence structure: Simple, short sentences with basic connectors (and, but)
            - Topics: Personal information, basic everyday activities, simple needs
            - Numbers 1-100, basic time expressions
            - Avoid any advanced structures, past tenses, conditional forms
        """,
        "A2": """
            A2 LEVEL GUIDELINES:
            - Vocabulary: Expanded everyday vocabulary (around 1500 words)
            - Grammar: Simple past tense, basic verb conjugation patterns
            - Sentence structure: Simple sentences with some coordination
            - Topics: Daily routines, shopping, local environment, simple past experiences
            - Simple descriptive adjectives
            - Avoid complex tenses, conditionals, complex clauses
        """,
        "B1": """
            B1 LEVEL GUIDELINES:
            - Vocabulary: More varied vocabulary (around 3000 words), some abstract terms
            - Grammar: Perfect and imperfect tenses, conditional mood, passive forms
            - Sentence structure: Compound sentences, simple subordination
            - Topics: Work, school, leisure, travel, current events, feelings
            - Comparative forms
            - Avoid literary language, complex constructions
        """,
        "B2": """
            B2 LEVEL GUIDELINES:
            - Vocabulary: Broader vocabulary (around 5000 words), some specialized terms
            - Grammar: All tense forms, more complex verbal constructions
            - Sentence structure: Complex sentences with various clause types
            - Topics: Social issues, professional topics, abstract concepts, hypothetical situations
            - Imperative forms, indirect speech
            - Avoid highly specialized terminology, dialectal expressions
        """,
        "C1": """
            C1 LEVEL GUIDELINES:
            - Vocabulary: Rich vocabulary (8000+ words), specialized terms, colloquial expressions
            - Grammar: All grammatical structures, including rare forms
            - Sentence structure: Sophisticated, complex sentences with embedded clauses
            - Topics: Any academic, professional or abstract topic, cultural references
            - Complex constructions, literary expressions
            - Nuanced differences in word meanings and connotations
            - Full range of language features
        """
    }
    
    # Language-specific guidelines
    language_specific = {
        "fin": {
            "A1": """
                FINNISH A1 SPECIFIC GUIDELINES:
                - Focus on nominative/partitive/genitive cases only
                - Simple consonant gradation patterns (kk-k, pp-p, tt-t)
                - Basic subject-verb agreement
                - Simple question particles and words
                - Personal pronouns (minä, sinä, hän, etc.)
            """,
            "A2": """
                FINNISH A2 SPECIFIC GUIDELINES:
                - Include inessive, elative, illative cases
                - All basic verb types
                - Standard consonant gradation patterns
                - Simple possessive suffixes
                - More extensive use of partitive case
            """,
            "B1": """
                FINNISH B1 SPECIFIC GUIDELINES:
                - All locative cases (also adessive, ablative, allative)
                - Object cases and their rules
                - Perfect and pluperfect tenses
                - Passive voice (present and past)
                - More complex uses of pronouns and demonstratives
            """,
            "B2": """
                FINNISH B2 SPECIFIC GUIDELINES:
                - Potential mood
                - Complex object rules
                - Multiple infinitive forms
                - Participles
                - Complex sentence structures
            """,
            "C1": """
                FINNISH C1 SPECIFIC GUIDELINES:
                - Complex participle constructions
                - Literary expressions and rare forms
                - Dialectal variations
                - Subtle case usage differences
                - Advanced idiomatic expressions
            """
        },
        "spa": {
            "A1": """
                SPANISH A1 SPECIFIC GUIDELINES:
                - Regular verb conjugations in present tense
                - Basic gender and number agreement
                - Simple prepositions
                - Question formation with intonation
                - Basic adjective placement
                - Common irregular verbs (ser, estar, ir, tener)
            """,
            "A2": """
                SPANISH A2 SPECIFIC GUIDELINES:
                - Preterite vs. imperfect tenses
                - Reflexive verbs
                - Direct and indirect object pronouns
                - Common irregular verbs
                - Comparative forms
                - Simple commands
            """,
            "B1": """
                SPANISH B1 SPECIFIC GUIDELINES:
                - Present subjunctive
                - Future and conditional tenses
                - Perfect tenses
                - Por vs. para distinctions
                - Relative pronouns
                - Formal commands
            """,
            "B2": """
                SPANISH B2 SPECIFIC GUIDELINES:
                - All subjunctive uses (present and imperfect)
                - Compound tenses
                - Passive structures
                - Advanced connecting phrases
                - Idiomatic expressions
                - Reported speech
            """,
            "C1": """
                SPANISH C1 SPECIFIC GUIDELINES:
                - Regional variations and dialectal features
                - Literary language
                - Complex hypothetical structures
                - Subtle tense distinctions
                - Cultural and historical references
                - Specialized vocabulary in various domains
            """
        },
        "fra": {
            "A1": """
                FRENCH A1 SPECIFIC GUIDELINES:
                - Regular -er verb conjugations
                - Basic irregular verbs (être, avoir, aller, faire)
                - Gender of nouns
                - Definite and indefinite articles
                - Basic prepositions
                - Question formation with est-ce que
                - Negation with ne...pas
            """,
            "A2": """
                FRENCH A2 SPECIFIC GUIDELINES:
                - Passé composé with avoir and être
                - Reflexive verbs
                - Direct and indirect object pronouns
                - Imperative mood
                - Futur proche (aller + infinitive)
                - Introduction to imparfait
                - Comparative forms
            """,
            "B1": """
                FRENCH B1 SPECIFIC GUIDELINES:
                - All past tenses (passé composé, imparfait, plus-que-parfait)
                - Future simple
                - Conditional present
                - Introduction to subjunctive
                - Relative pronouns (qui, que, où, dont)
                - Passive voice
                - Reported speech
            """,
            "B2": """
                FRENCH B2 SPECIFIC GUIDELINES:
                - Advanced subjunctive uses
                - Conditional past
                - Literary tenses (recognition)
                - Complex pronouns (y, en, lequel)
                - Advanced connecting expressions
                - Nominalizations
                - Idiomatic expressions
            """,
            "C1": """
                FRENCH C1 SPECIFIC GUIDELINES:
                - Literary tenses (passé simple, subjonctif imparfait)
                - Complex hypothetical structures
                - Advanced nominalizations
                - Stylistic variations
                - Regional expressions
                - Linguistic nuances and connotations
                - Specialized terminology
            """
        },
        "deu": {
            "A1": """
                GERMAN A1 SPECIFIC GUIDELINES:
                - Present tense regular and irregular verbs
                - Word order in main clauses
                - Nominative and accusative cases
                - Modal verbs
                - Definite and indefinite articles
                - Question formation
                - Negation with nicht and kein
            """,
            "A2": """
                GERMAN A2 SPECIFIC GUIDELINES:
                - Perfect tense
                - Dative case
                - Prepositions with fixed case
                - Imperative forms
                - Possessive articles
                - Comparative and superlative
                - Subordinate clauses with weil, dass, wenn
            """,
            "B1": """
                GERMAN B1 SPECIFIC GUIDELINES:
                - Genitive case
                - Adjective declension
                - Simple passive voice
                - Subjunctive II (würde + infinitive, hätte, wäre)
                - Relative clauses
                - Temporal prepositions and conjunctions
                - Future tense
            """,
            "B2": """
                GERMAN B2 SPECIFIC GUIDELINES:
                - Konjunktiv I (reported speech)
                - Extended passive voice (with modal verbs)
                - N-declension nouns
                - Participle constructions
                - Advanced connecting phrases
                - Extended attributes
                - Advanced subordinate clauses
            """,
            "C1": """
                GERMAN C1 SPECIFIC GUIDELINES:
                - Advanced verbal constructions
                - All passive and subjunctive forms
                - Nominalized verbs
                - Literary and formal expressions
                - Idiomatic expressions and collocations
                - Regional variations
                - Complex sentence structures
            """
        },
        "ita": {
            "A1": """
                ITALIAN A1 SPECIFIC GUIDELINES:
                - Present tense of regular verbs (-are, -ere, -ire)
                - Common irregular verbs (essere, avere, fare, andare)
                - Definite and indefinite articles
                - Noun gender and number
                - Basic adjective agreement
                - Simple prepositions
                - Question formation
            """,
            "A2": """
                ITALIAN A2 SPECIFIC GUIDELINES:
                - Passato prossimo with avere and essere
                - Introduction to imperfetto
                - Reflexive verbs
                - Direct object pronouns
                - Comparative forms
                - Future tense (introduction)
                - Modal verbs (dovere, potere, volere)
            """,
            "B1": """
                ITALIAN B1 SPECIFIC GUIDELINES:
                - Contrasting imperfetto and passato prossimo
                - Future tense
                - Conditional present
                - Introduction to congiuntivo
                - Combined pronouns
                - Relative pronouns (che, cui, quale)
                - Introduction to passive voice
            """,
            "B2": """
                ITALIAN B2 SPECIFIC GUIDELINES:
                - All subjunctive tenses
                - Passato remoto (recognition)
                - Conditional past
                - Advanced pronoun usage
                - Passive constructions
                - Gerund and participle forms
                - Complex connecting expressions
            """,
            "C1": """
                ITALIAN C1 SPECIFIC GUIDELINES:
                - Literary tenses
                - Complex sentence structures
                - Stylistic variations
                - Idiomatic expressions
                - Regional language variations
                - Advanced formal registers
                - Specialized terminology
            """
        },
        "rus": {
            "A1": """
                RUSSIAN A1 SPECIFIC GUIDELINES:
                - Cyrillic alphabet and pronunciation
                - Present tense of common verbs
                - Gender of nouns
                - Personal and possessive pronouns
                - Nominative case
                - Simple questions
                - Numerals 1-100
            """,
            "A2": """
                RUSSIAN A2 SPECIFIC GUIDELINES:
                - Past tense
                - Future tense (imperfective and simple perfective)
                - Introduction to cases (accusative, prepositional)
                - Basic aspects of verbs
                - Possessive pronouns
                - Adjective agreement
                - More question types
            """,
            "B1": """
                RUSSIAN B1 SPECIFIC GUIDELINES:
                - All cases (nominative, accusative, genitive, dative, instrumental, prepositional)
                - Verbal aspects (perfective and imperfective)
                - Basic verbs of motion
                - Imperatives
                - Conditional expressions
                - Complex sentence structures
                - Time expressions
            """,
            "B2": """
                RUSSIAN B2 SPECIFIC GUIDELINES:
                - Verbs of motion with prefixes
                - Participles and verbal adverbs (introduction)
                - Passive constructions
                - Complex sentences
                - Advanced use of cases
                - Numerals and counting
                - Formal and informal registers
            """,
            "C1": """
                RUSSIAN C1 SPECIFIC GUIDELINES:
                - Complex verbal constructions
                - Advanced participles and verbal adverbs
                - Nuanced aspects usage
                - Idiomatic expressions
                - Stylistic variations
                - Language of literature and media
                - Dialectal features
            """
        },
        "swe": {
            "A1": """
                SWEDISH A1 SPECIFIC GUIDELINES:
                - Present tense of regular verbs
                - Common irregular verbs (är, har, gör)
                - En/ett gender system
                - Indefinite and definite forms of nouns
                - Personal pronouns
                - Word order in main clauses
                - Simple questions
            """,
            "A2": """
                SWEDISH A2 SPECIFIC GUIDELINES:
                - Past tense (preteritum)
                - Present perfect (perfekt)
                - Adjective agreement
                - Modal verbs
                - Adverbs and word order
                - Possessive pronouns
                - Comparative forms
            """,
            "B1": """
                SWEDISH B1 SPECIFIC GUIDELINES:
                - Future constructions
                - Conditional forms
                - Subordinate clauses and word order
                - Relative clauses
                - Passive voice
                - Reflexive verbs
                - Particles and phrasal verbs
            """,
            "B2": """
                SWEDISH B2 SPECIFIC GUIDELINES:
                - Past perfect (pluskvamperfekt)
                - Subjunctive in fixed expressions
                - Advanced subordinate clauses
                - Extended attributes
                - S-passiv vs. bli-passiv
                - Advanced connecting expressions
                - Formal language
            """,
            "C1": """
                SWEDISH C1 SPECIFIC GUIDELINES:
                - Complex verbal constructions
                - Advanced word order variations
                - Stylistic nuances
                - Idiomatic expressions
                - Regional language variations
                - Literary language
                - Specialized terminology
            """
        }
    }
    
    # Start with base guidelines
    guidelines = base_guidelines.get(level_code, "")
    
    # Add language-specific guidelines if available
    if language_code in language_specific and level_code in language_specific[language_code]:
        guidelines += language_specific[language_code][level_code]
    
    return guidelines

# Function to convert chat history to Markdown format
def get_chat_history_markdown(session_state):
    """
    Convert the chat history to a Markdown string format with level indicators
    """
    # Get language info if available
    lang_code = session_state.selected_language if hasattr(session_state, 'selected_language') else "fra"
    lang_name = "French"  # Default
    
    # Try to get language name from app.py's SUPPORTED_LANGUAGES
    try:
        import app
        if hasattr(app, 'SUPPORTED_LANGUAGES') and lang_code in app.SUPPORTED_LANGUAGES:
            lang_name = app.SUPPORTED_LANGUAGES[lang_code]["name"]
    except:
        # If you can't import, use a basic mapping
        lang_mapping = {
            "fin": "Finnish",
            "spa": "Spanish",
            "fra": "French",
            "deu": "German",
            "ita": "Italian",
            "jpn": "Japanese",
            "zho": "Chinese",
            "rus": "Russian"
        }
        lang_name = lang_mapping.get(lang_code, "Unknown")
    
    markdown_text = f"# Polyglot {lang_name} Language Tutor - Chat History\n\n"
    markdown_text += f"Session ID: {session_state.session_id}\n"
    markdown_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    markdown_text += f"Language: {lang_name}\n"
    markdown_text += f"Current Proficiency Level: {session_state.selected_level}\n\n"
    
    # Add level history if available
    if hasattr(session_state, 'level_history') and session_state.level_history:
        markdown_text += "## Level Progression\n\n"
        for change in session_state.level_history:
            lang = change.get('language', lang_code)
            lang_display = ""
            try:
                import app
                if hasattr(app, 'SUPPORTED_LANGUAGES') and lang in app.SUPPORTED_LANGUAGES:
                    lang_display = f" ({app.SUPPORTED_LANGUAGES[lang]['name']})"
            except:
                pass
            
            markdown_text += f"- Changed from {change['from']} to {change['to']} on {change['timestamp']}{lang_display}\n"
        markdown_text += "\n"
    
    markdown_text += "---\n\n"
    
    for message in session_state.chat_history:
        timestamp = message.get("timestamp", "")
        if message["role"] == "user":
            markdown_text += f"## User ({timestamp})\n\n"
            markdown_text += f"{message['content']}\n\n"
        else:
            # Try to determine what level this message was at
            level = "Unknown"
            if hasattr(message, 'level'):
                level = message.get('level', session_state.selected_level)
            
            markdown_text += f"## Tutor - {level} ({timestamp})\n\n"
            markdown_text += f"{message['content']}\n\n"
        markdown_text += "---\n\n"
    
    return markdown_text

# Extract and track topics from user messages
def extract_topics(message, current_topics):
    """
    Extract potential learning topics from user messages using LLM to personalize future exercises
    
    Parameters:
    - message: User's message text
    - current_topics: List of previously identified topics
    
    Returns:
    - Updated list of topics
    """
    # If message is too short, return current topics unchanged
    if not message or len(message.strip()) < 10:
        return current_topics
    
    try:
        # Try to use LLM for topic extraction
        new_topics = extract_topics_llm(message)
        
        # Add new topics to current list, avoiding duplicates
        updated_topics = current_topics.copy()
        for topic in new_topics:
            if topic and topic not in updated_topics:
                updated_topics.append(topic)
        
        # Keep list at reasonable size
        if len(updated_topics) > 30:
            updated_topics = updated_topics[-30:]
            
        return updated_topics
        
    except Exception as e:
        # Fallback to simplified rule-based method if LLM fails
        import logging
        logging.warning(f"LLM topic extraction failed: {str(e)}. Using rule-based method.")
        
        # Simplified rule-based fallback (similar to original implementation)
        # Look for potential words excluding common stopwords
        import re
        words = re.findall(r'\b[a-zA-Z\u00C0-\u00FF\u0100-\u017F\u0180-\u024F\u0370-\u03FF\u0400-\u04FF]{4,}\b', 
                         message.lower())
        
        # Basic stopwords to filter out
        stopwords = {"about", "after", "all", "also", "and", "any", "because", "but", "can", "come", "could", 
                    "day", "even", "first", "from", "get", "give", "have", "here", "him", "his", "how", 
                    "into", "its", "just", "know", "like", "look", "make", "many", "more", "most", "much", 
                    "must", "new", "now", "one", "only", "other", "our", "out", "over", "people", "say", 
                    "see", "she", "some", "take", "than", "that", "the", "their", "them", "then", "there", 
                    "these", "they", "think", "this", "time", "two", "use", "very", "want", "way", "well", 
                    "what", "when", "which", "who", "will", "with", "would", "your"}
        
        # Filter out stopwords
        filtered_words = [word for word in words if word not in stopwords]
        
        # Grammar terms to specifically look for
        grammar_terms = re.findall(r'\b(verb|noun|case|tense|plural|singular|adjective|adverb|conjugation|particle|preposition|article|gender|declension)\b', 
                                message.lower())
        
        # Learning-related terms to specifically look for
        learning_terms = re.findall(r'\b(exercise|translate|vocabulary|grammar|pronunciation|reading|writing|speaking|listening)\b', 
                                   message.lower())
        
        # Combine filtered words with grammar and learning terms
        all_topics = filtered_words + grammar_terms + learning_terms
        
        # Add new topics to current list, avoiding duplicates
        updated_topics = current_topics.copy()
        for topic in all_topics:
            if topic not in updated_topics:
                updated_topics.append(topic)
        
        # Keep list at reasonable size
        if len(updated_topics) > 30:
            updated_topics = updated_topics[-30:]
            
        return updated_topics

# Use caching for LLM-based topic extraction to improve performance
import functools

@functools.lru_cache(maxsize=100)
def extract_topics_llm(message):
    """
    Extract learning topics from message using LLM with caching
    """
    # Import required libraries
    from langchain_openai import ChatOpenAI
    import streamlit as st
    import json
    import re
    
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OpenAI API key not configured in Streamlit secrets")
    
    # Initialize the LLM
    model_name = st.secrets.get("MODEL_NAME", "gpt-4.1-mini-2025-04-14")
    chat = ChatOpenAI(
        openai_api_key=api_key,
        model=model_name,
        max_tokens=150  # Small context for topic extraction
    )
    
    # Get current language and level if available
    current_language = "unknown"
    current_level = "unknown"
    try:
        if hasattr(st.session_state, 'selected_language'):
            language_code = st.session_state.selected_language
            import app
            if hasattr(app, 'SUPPORTED_LANGUAGES') and language_code in app.SUPPORTED_LANGUAGES:
                current_language = app.SUPPORTED_LANGUAGES[language_code]["name"]
        
        if hasattr(st.session_state, 'selected_level'):
            current_level = st.session_state.selected_level
    except:
        pass
    
    # Prepare the prompt
    prompt = [
        {
            "role": "system", 
            "content": f"""You are a topic extraction system for a language learning application.
            Extract meaningful learning topics from the user's message that can be used to personalize future exercises.
            
            The user is learning {current_language} at {current_level} level.
            
            Focus on extracting:
            1. Grammar concepts mentioned (e.g., verb tenses, cases, pronouns)
            2. Vocabulary themes (e.g., food, travel, work)
            3. Language skills (e.g., reading, writing, pronunciation)
            4. Specific linguistic features of {current_language}
            5. Learning goals or interests
            
            Return a JSON array of 2-8 topics, with each topic being a single word or short phrase.
            Example: ["past tense", "food vocabulary", "pronunciation", "travel"]
            
            Only extract topics that are actually present in the message. If no clear topics are found, return an empty array.
            """
        },
        {
            "role": "user",
            "content": f"Extract learning topics from this message: \"{message}\""
        }
    ]
    
    # Get the response from the LLM
    response = chat.invoke(prompt)
    response_content = response.content.strip()
    
    # Try to parse the response as JSON
    try:
        # Extract JSON array if embedded in text
        json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
        if json_match:
            topics = json.loads(json_match.group(0))
        else:
            # Try parsing the whole response as JSON
            topics = json.loads(response_content)
        
        # Ensure it's a list
        if not isinstance(topics, list):
            topics = []
        
    except:
        # If parsing fails, extract topics using simple regex
        topics = re.findall(r'"([^"]+)"', response_content)
        if not topics:
            # Try without quotes
            topics = [t.strip() for t in response_content.split(",") if t.strip()]
    
    # Filter out any non-string items and convert to lowercase
    topics = [str(topic).lower() for topic in topics if topic]
    
    return topics

# Function to process user messages
def process_question(question, session_state):
    """
    Process a user message, update topic tracking, and generate assistant response
    """
    # Get current level code
    current_level = session_state.selected_level
    level_code = current_level.split()[0]  # A1, A2, etc.
    
    # Get current language
    lang_code = session_state.selected_language if hasattr(session_state, 'selected_language') else "fin"
    
    # Add user question to the chat
    session_state.messages.append({"role": "user", "content": question})
    session_state.chat_history.append({
        "role": "user", 
        "content": question, 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": current_level,  # Track level at time of message
        "language": lang_code    # Track language at time of message
    })
    
    # Extract topics from the user message
    session_state.user_topics = extract_topics(question, session_state.user_topics)
    
    # Set chat as started
    session_state.chat_started = True
    
    # Get AI response
    response = call_openai_api(session_state)
    
    # Add assistant response to chat
    session_state.messages.append({"role": "assistant", "content": response})
    session_state.chat_history.append({
        "role": "assistant", 
        "content": response, 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": current_level,  # Track level at time of message
        "language": lang_code    # Track language at time of message
    })
    
    # Reset level and language change flags if they were set
    if hasattr(session_state, 'current_level_changed') and session_state.current_level_changed:
        session_state.current_level_changed = False
    if hasattr(session_state, 'language_changed') and session_state.language_changed:
        session_state.language_changed = False

# Function to get MIME type description
def get_file_type_description(mime_type):
    """
    Get a user-friendly description of a file based on its MIME type
    """
    mime_descriptions = {
        "text/plain": "text file",
        "text/csv": "CSV spreadsheet",
        "text/html": "HTML document",
        "text/markdown": "Markdown document",
        "application/pdf": "PDF document",
        "application/json": "JSON file",
        "application/xml": "XML document",
        "application/msword": "Word document",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word document",
        "application/vnd.ms-excel": "Excel spreadsheet",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel spreadsheet",
        "application/vnd.ms-powerpoint": "PowerPoint presentation",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint presentation",
        "image/jpeg": "JPEG image",
        "image/png": "PNG image",
        "image/gif": "GIF image",
        "image/svg+xml": "SVG image",
        "audio/mpeg": "MP3 audio file",
        "audio/wav": "WAV audio file",
        "video/mp4": "MP4 video file"
    }
    
    # Check if we have a specific description, otherwise use the generic MIME type
    if mime_type in mime_descriptions:
        return mime_descriptions[mime_type]
    elif mime_type.split('/')[0] in ["text", "application", "image", "audio", "video"]:
        return f"{mime_type.split('/')[0]} file"
    else:
        return "file"

# Function to get language display name
def get_language_display_name(lang_code):
    """
    Get the display name for a language code
    """
    try:
        # Try to import app.py to get language info
        import app
        if hasattr(app, 'SUPPORTED_LANGUAGES') and lang_code in app.SUPPORTED_LANGUAGES:
            return app.SUPPORTED_LANGUAGES[lang_code]["name"]
    except:
        # Fallback if import fails
        language_names = {
            "fin": "Finnish",
            "spa": "Spanish",
            "fra": "French",
            "deu": "German",
            "ita": "Italian",
            "jpn": "Japanese",
            "zho": "Chinese",
            "rus": "Russian",
            "ara": "Arabic",
            "por": "Portuguese",
            "hin": "Hindi",
            "swe": "Swedish",
            "nld": "Dutch",
            "tur": "Turkish"
        }
        return language_names.get(lang_code, "Unknown")

# Function to get language flag emoji
def get_language_flag(lang_code):
    """
    Get the flag emoji for a language code
    """
    try:
        # Try to import app.py to get language info
        import app
        if hasattr(app, 'SUPPORTED_LANGUAGES') and lang_code in app.SUPPORTED_LANGUAGES:
            return app.SUPPORTED_LANGUAGES[lang_code]["flag"]
    except:
        # Fallback if import fails
        language_flags = {
            "fin": "🇫🇮",
            "spa": "🇪🇸",
            "fra": "🇫🇷",
            "deu": "🇩🇪",
            "ita": "🇮🇹",
            "jpn": "🇯🇵",
            "zho": "🇨🇳",
            "rus": "🇷🇺",
            "ara": "🇸🇦",
            "por": "🇵🇹",
            "hin": "🇮🇳",
            "swe": "🇸🇪",
            "nld": "🇳🇱",
            "tur": "🇹🇷"
        }
        return language_flags.get(lang_code, "🌍")

def get_llm(session_state, streaming=True):
    """
    Get the appropriate LLM based on session state model provider selection.

    Args:
        session_state: Streamlit session state
        streaming: Whether to enable streaming (default: True)

    Returns:
        ChatOpenAI or ChatOllama instance
    """
    model_provider = getattr(session_state, 'model_provider', 'openai')

    if model_provider == "ollama":
        # Use Ollama for free local models
        model_name = getattr(session_state, 'ollama_model', 'phi3')
        return ChatOllama(
            model=model_name,
            temperature=0.7,
        )
    else:
        # Use OpenAI (default)
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        model_name = st.secrets.get("MODEL_NAME", "gpt-4.1-mini-2025-04-14")
        max_tokens = st.secrets.get("MAX_TOKENS", 8000)

        if not api_key:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .streamlit/secrets.toml or switch to Ollama in the sidebar.")

        return ChatOpenAI(
            openai_api_key=api_key,
            model=model_name,
            max_tokens=max_tokens,
            streaming=streaming
        )

# Function to call OpenAI API using LangChain's ChatOpenAI
def call_openai_api(session_state):
    try:
        # Get the appropriate LLM based on session state
        chat = get_llm(session_state, streaming=True)
        
        # Get current level and code
        level = session_state.selected_level
        level_code = level.split()[0]  # Extract just the level code (A1, A2, etc.)
        
        # Get current language
        lang_code = session_state.selected_language if hasattr(session_state, 'selected_language') else "fin"
        lang_name = get_language_display_name(lang_code)
        lang_flag = get_language_flag(lang_code)
        
        # Get level-appropriate content guidelines
        level_content = get_level_appropriate_content(level_code, lang_code)
        
        # Get CEFR level guidelines
        cefr_guidelines = get_cefr_level_guidelines(level_code, lang_code)
        
        # Create a detailed level-specific and language-specific prompt
        specific_prompt = SYSTEM_PROMPT + f"""

## CURRENT LEARNER LANGUAGE: {lang_flag} {lang_name}
## CURRENT LEARNER LEVEL: {level} 
{cefr_guidelines}

VOCABULARY GUIDELINES FOR {lang_name} {level_code}:
{', '.join(level_content.get('vocabulary', ['No specific vocabulary guidelines available']))}

GRAMMAR GUIDELINES FOR {lang_name} {level_code}:
{', '.join(level_content.get('grammar', ['No specific grammar guidelines available']))}

EXAMPLE SENTENCES FOR {lang_name} {level_code}:
{' '.join(level_content.get('example_sentences', ['No example sentences available']))}

YOU MUST STRICTLY ADHERE TO THESE GUIDELINES FOR {lang_name} {level_code} LEVEL:
1. ONLY use vocabulary appropriate for {level_code} level
2. ONLY use grammar structures appropriate for {level_code} level
3. Keep explanations appropriate for {level_code} level complexity
4. Format your responses clearly with the level indicator

Remember: Always visually include the {level_code} level indicator in your responses using a badge or highlight.
"""
        
        # Add personalization based on user topics if available
        if session_state.user_topics and len(session_state.user_topics) > 0:
            topics_str = ", ".join(session_state.user_topics[-10:])  # Use last 10 topics for relevance
            specific_prompt += f"\n\nThe learner has shown interest in these topics: {topics_str}. Try to incorporate these topics into examples and exercises when appropriate to personalize the learning experience. Remember to ONLY use vocabulary and grammar structures appropriate for {level_code} level when incorporating these topics."
        
        # Add level history information if available
        if hasattr(session_state, 'level_history') and session_state.level_history:
            # If user has changed levels, provide context
            specific_prompt += "\n\nLevel progression history:"
            for change in session_state.level_history[-3:]:  # Last 3 changes
                change_lang = change.get('language', lang_code)
                change_lang_name = get_language_display_name(change_lang)
                specific_prompt += f"\n- Changed from {change['from']} to {change['to']} on {change['timestamp']} for {change_lang_name}"
            
            # If user recently moved up, note potential need for review
            if session_state.level_history and len(session_state.level_history) > 0:
                last_change = session_state.level_history[-1]
                prev_level_code = last_change['from'].split()[0]
                curr_level_code = last_change['to'].split()[0]
                
                # Check if this is a move up the CEFR scale
                cefr_progression = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}
                
                if cefr_progression.get(prev_level_code, 0) < cefr_progression.get(curr_level_code, 0):
                    specific_prompt += f"""
                    \n\nIMPORTANT: The learner recently progressed from {prev_level_code} to {curr_level_code}. 
                    This means:
                    1. Occasionally include review material from {prev_level_code} level
                    2. Focus primarily on {curr_level_code} level content
                    3. Build bridges between what they already know and new concepts
                    4. Give extra encouragement when they master new {curr_level_code} level structures
                    """
        
        # Check if level was recently changed
        if hasattr(session_state, 'current_level_changed') and session_state.current_level_changed:
            specific_prompt += f"""
            \n\nALERT: The learner JUST changed their level to {level_code}. In your next response:
            1. Acknowledge this level change explicitly
            2. Briefly explain what {level_code} level means for {lang_name} learning
            3. Give a short example of appropriate content for this level
            4. Be encouraging about their language learning journey
            """
        
        # Check if language was recently changed
        if hasattr(session_state, 'language_changed') and session_state.language_changed:
            specific_prompt += f"""
            \n\nALERT: The learner JUST changed their language to {lang_name}. In your next response:
            1. Acknowledge this language change explicitly
            2. Include a brief, appropriate greeting in {lang_name}
            3. Briefly explain how you'll adapt to teaching {lang_name} at their {level_code} level
            4. Be encouraging about their decision to learn {lang_name}
            """
        
        formatted_messages = [{"role": "system", "content": specific_prompt}]
        
        # Add conversation history
        for msg in session_state.messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add file if present and it's a recent upload (check if it's in the last message)
        if session_state.uploaded_file:
            # Check if the file was just uploaded (mentioned in the last assistant message)
            last_assistant_message = None
            for msg in reversed(session_state.messages):
                if msg["role"] == "assistant":
                    last_assistant_message = msg["content"]
                    break
            
            if last_assistant_message and "has been uploaded" in last_assistant_message:
                # Create a message about the uploaded file with explicit level instructions
                level_code = session_state.selected_level.split()[0]  # Extract just the level code (A1, A2, etc.)
                
                # Get a friendly file type description
                file_type_desc = get_file_type_description(session_state.uploaded_file['type'])
                
                # Different handling based on file type
                if session_state.uploaded_file['type'].startswith('image/'):
                    # For images, use image_url parameter
                    file_message = {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": f"Here's an image I've uploaded. I'm learning {lang_name} at {session_state.selected_level} level. Please extract any {lang_name} text from it, translate it, and create exercises based on it that are STRICTLY appropriate for {level_code} level students. Ensure all vocabulary and grammar is EXACTLY at {level_code} level complexity - do not use any structures or words from higher levels."},
                            {"type": "image_url", "image_url": {"url": f"data:{session_state.uploaded_file['type']};base64,{session_state.uploaded_file['base64']}"}}
                        ]
                    }
                elif session_state.uploaded_file.get('is_text_file', False) and session_state.uploaded_file.get('text_content'):
                    # For text files, include the content directly
                    file_message = {
                        "role": "user",
                        "content": f"Here's a {file_type_desc} I've uploaded named '{session_state.uploaded_file['name']}'. I'm learning {lang_name} at {session_state.selected_level} level. Here's the content of the file:\n\n```\n{session_state.uploaded_file['text_content']}\n```\n\nPlease analyze this text, translate any {lang_name} content, explain grammar concepts, and create exercises based on it that are STRICTLY appropriate for {level_code} level students. Ensure all vocabulary and grammar is EXACTLY at {level_code} level complexity - do not use any structures or words from higher levels."
                    }
                else:
                    # For other file types, just describe the file
                    file_message = {
                        "role": "user",
                        "content": f"I've uploaded a {file_type_desc} named '{session_state.uploaded_file['name']}'. I'm learning {lang_name} at {session_state.selected_level} level. Please help me learn {lang_name} from this file by creating appropriate exercises and content for {level_code} level students. Ensure all vocabulary and grammar is EXACTLY at {level_code} level complexity - do not use any structures or words from higher levels."
                    }
                
                formatted_messages.append(file_message)
        
        # Set up placeholder for streaming
        placeholder = st.empty()
        collected_content = ""
        
        # Add visual level badge to responses
        level_badge = format_level_badge(level_code)
        
        # Process streaming response
        for chunk in chat.stream(formatted_messages):
            if chunk.content:
                collected_content += chunk.content
                
                # Check if level badge is already in the content
                if not collected_content.startswith('<span class="level-badge'):
                    display_content = f"{level_badge} {collected_content}"
                else:
                    display_content = collected_content
                
                placeholder.markdown(f"""
                <div class="chat-message assistant">
                    <div class="avatar">{lang_flag}</div>
                    <div class="message">{display_content}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Add level badge to the beginning of the response if it's not already there
        if not collected_content.startswith('<span class="level-badge'):
            return f"{level_badge} {collected_content}"
        else:
            return collected_content
    
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return f"I'm sorry, there was an error processing your request: {str(e)}. Please try again."

