# -----------------------------
# Import required Python modules
# -----------------------------
import html
import json
import os
import re
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# ---------------------------------------------------
# Load environment variables from the local .env file
# ---------------------------------------------------
load_dotenv()

# -----------------------------
# Main application configuration
# -----------------------------
# This title is used by Streamlit for the browser tab.
APP_TITLE = "AI Tech Support Assistant"

# This is the Groq model used to generate the technical support answer.
GROQ_MODEL = "llama-3.1-8b-instant"

# External CSS file used to customize the Streamlit interface.
STYLE_FILE = Path("styles.css")

# Regular expression range for detecting Arabic characters.
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")


# -----------------------------------------
# Streamlit page setup and browser metadata
# -----------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":computer:",
    layout="centered",
)


# --------------------------------------------------------
# Application text for both English and Arabic interfaces
# --------------------------------------------------------
# Keeping all labels in one dictionary makes the UI easier to translate
# and prevents duplicated text throughout the application.
TEXT = {
    "en": {
        "language_name": "English",
        "title": "AI Tech Support Assistant",
        "description": (
            "Describe a technology problem and get possible causes, safe "
            "troubleshooting steps, a risk level, and a practical recommendation."
        ),
        "examples_title": "Examples",
        "input_placeholder": "Type your technical problem and press Enter...",
        "empty_warning": "Please write a technical problem first.",
        "thinking": "Analyzing the problem...",
        "missing_key": "Missing Groq API key. Add GROQ_API_KEY to your .env file.",
        "missing_key_help": "Create a .env file in the project folder and add your Groq API key.",
        "format_error": "The AI response could not be formatted correctly. Please try again.",
        "api_error": "The API request failed. Please check your API key and internet connection.",
        "technical_details": "Technical details",
        "summary": "Problem Summary",
        "causes": "Possible Causes",
        "solutions": "Step-by-Step Solutions",
        "risk": "Risk Level",
        "recommendation": "Helpful Recommendation",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "clear": "Clear chat",
        "assistant_greeting": (
            "Hello. Tell me what technology problem you are facing, and I will "
            "help you troubleshoot it step by step."
        ),
        "examples": [
            "My laptop is very slow",
            "My WiFi disconnects frequently",
            "My phone overheats while charging",
            "My printer is not printing",
            "My computer screen is black",
        ],
    },
    "ar": {
        "language_name": "العربية",
        "title": "مساعد الدعم التقني بالذكاء الاصطناعي",
        "description": (
            "اكتب المشكلة التقنية التي تواجهك لتحصل على الأسباب المحتملة، "
            "خطوات حل آمنة، مستوى الخطورة، وتوصية مناسبة."
        ),
        "examples_title": "أمثلة",
        "input_placeholder": "اكتب مشكلتك التقنية واضغط Enter...",
        "empty_warning": "يرجى كتابة المشكلة التقنية أولا.",
        "thinking": "جاري تحليل المشكلة...",
        "missing_key": "مفتاح Groq API غير موجود. أضف GROQ_API_KEY إلى ملف .env.",
        "missing_key_help": "أنشئ ملف .env داخل مجلد المشروع ثم أضف مفتاح Groq API.",
        "format_error": "تعذر تنسيق رد الذكاء الاصطناعي بشكل صحيح. يرجى المحاولة مرة أخرى.",
        "api_error": "فشل طلب API. يرجى التحقق من مفتاح API والاتصال بالإنترنت.",
        "technical_details": "التفاصيل التقنية",
        "summary": "ملخص المشكلة",
        "causes": "الأسباب المحتملة",
        "solutions": "خطوات الحل",
        "risk": "مستوى الخطورة",
        "recommendation": "توصية مفيدة",
        "low": "منخفض",
        "medium": "متوسط",
        "high": "مرتفع",
        "clear": "مسح المحادثة",
        "assistant_greeting": (
            "مرحبا. اكتب المشكلة التقنية التي تواجهك، وسأساعدك في حلها خطوة بخطوة."
        ),
        "examples": [
            "جهازي المحمول بطيء جدا",
            "الواي فاي ينقطع كثيرا",
            "هاتفي يسخن أثناء الشحن",
            "الطابعة لا تطبع",
            "شاشة الكمبيوتر سوداء",
        ],
    },
}


# ----------------------------
# System prompt for the AI LLM
# ----------------------------
# This prompt defines the assistant role, safety rules, language behavior,
# and required JSON response format.
SYSTEM_PROMPT = """
You are a professional IT support assistant for beginner users.

Your job is to analyze common technology problems and provide safe,
clear, practical troubleshooting advice.

Language rules:
- Answer in the same language used by the user's problem.
- If the user writes in Arabic, all JSON values must be in Arabic.
- If the user writes in English, all JSON values must be in English.
- Ignore the application's UI language when choosing the response language.

Safety rules:
- Do not provide dangerous electrical, battery, or hardware repair instructions.
- Do not ask users to open power supplies, chargers, batteries, or sealed devices.
- If the issue may be serious, hardware-related, electrical, overheating,
  data-loss related, or unsafe, advise the user to contact a qualified technician.
- Keep the explanation easy for beginners to understand.
- Do not invent certainty. Mention when a cause is only a possibility.

Return only valid JSON using this exact structure:
{
  "problem_summary": "short summary",
  "possible_causes": ["cause 1", "cause 2", "cause 3"],
  "step_by_step_solutions": ["step 1", "step 2", "step 3"],
  "risk_level": "Low or Medium or High",
  "helpful_recommendation": "final recommendation"
}
"""


def contains_arabic(text):
    """Return True when the given text contains Arabic characters."""
    return bool(ARABIC_RE.search(text))


def text_direction(text):
    """Return rtl for Arabic text and ltr for English or other text."""
    return "rtl" if contains_arabic(text) else "ltr"


def current_language():
    """Get the selected UI language from Streamlit session state."""
    return st.session_state.get("ui_language", "en")


def current_labels():
    """Return all labels for the currently selected UI language."""
    return TEXT[current_language()]


def has_user_messages():
    """Check whether the user has already sent at least one message."""
    return any(message.get("role") == "user" for message in st.session_state.messages)


def init_session_state():
    """Create default values that must persist while the app is running."""
    # ui_language stores the chosen interface language.
    st.session_state.setdefault("ui_language", "en")

    # messages stores the full chat history as a list of dictionaries.
    st.session_state.setdefault("messages", [])


def load_styles(page_direction, align_side):
    """Load the CSS file and inject language direction values into it."""
    # The CSS file contains placeholders because Arabic and English need
    # different page direction and alignment values.
    css = STYLE_FILE.read_text(encoding="utf-8")
    css = css.replace("__PAGE_DIRECTION__", page_direction)
    css = css.replace("__ALIGN_SIDE__", align_side)

    # unsafe_allow_html is required because Streamlit normally escapes style tags.
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def get_groq_client():
    """Create and return the Groq client if the API key exists."""
    # The API key must be stored in .env as GROQ_API_KEY.
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    # The key is passed to the Groq SDK, not written directly in the code.
    return Groq(api_key=api_key)


def analyze_problem(problem_text):
    """Send the user's problem to Groq and return parsed JSON analysis."""
    client = get_groq_client()
    if client is None:
        raise ValueError("missing_key")

    # The Groq API receives a system prompt plus the user's technical problem.
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Analyze this technical problem:\n\n{problem_text}",
            },
        ],
        temperature=0.3,
        # JSON response format makes the AI output easier to display in sections.
        response_format={"type": "json_object"},
    )

    # Parse the JSON string returned by the AI into a Python dictionary.
    content = response.choices[0].message.content
    return json.loads(content)


def risk_class(risk_level):
    """Convert a risk level into a CSS class name."""
    normalized = risk_level.strip().lower()
    if normalized in ["low", "منخفض"]:
        return "risk-low"
    if normalized in ["medium", "متوسط"]:
        return "risk-medium"
    if normalized in ["high", "مرتفع", "عالي"]:
        return "risk-high"
    return "risk-medium"


def localized_risk(risk_level, language):
    """Translate the risk level label based on the response language."""
    normalized = risk_level.strip().lower()
    if normalized in ["low", "منخفض"]:
        return TEXT[language]["low"]
    if normalized in ["medium", "متوسط"]:
        return TEXT[language]["medium"]
    if normalized in ["high", "مرتفع", "عالي"]:
        return TEXT[language]["high"]
    return risk_level


def render_list(items, ordered=False):
    """Render a Python list as an HTML ordered or unordered list."""
    # Ordered lists are used for solution steps.
    # Unordered lists are used for possible causes.
    tag = "ol" if ordered else "ul"
    list_items = "".join(f"<li>{html.escape(str(item))}</li>" for item in items)
    return f"<{tag}>{list_items}</{tag}>"


def render_analysis(analysis, labels, direction, response_language):
    """Convert the model JSON into a formatted HTML card."""
    # Read each expected section from the AI JSON response.
    causes = analysis.get("possible_causes", [])
    solutions = analysis.get("step_by_step_solutions", [])
    risk_level = str(analysis.get("risk_level", "Unknown"))

    # Escape AI text before inserting it into HTML for safer rendering.
    summary = html.escape(str(analysis.get("problem_summary", "")))
    recommendation = html.escape(str(analysis.get("helpful_recommendation", "")))
    risk_text = html.escape(localized_risk(risk_level, response_language))

    # The returned HTML becomes the assistant message bubble content.
    return (
        f'<div class="analysis-card" dir="{direction}">'
        f'<h4>{labels["summary"]}</h4>'
        f"<p>{summary}</p>"
        f'<h4>{labels["causes"]}</h4>'
        f"{render_list(causes)}"
        f'<h4>{labels["solutions"]}</h4>'
        f"{render_list(solutions, ordered=True)}"
        f'<h4>{labels["risk"]}</h4>'
        f'<span class="risk-pill {risk_class(risk_level)}">{risk_text}</span>'
        f'<h4>{labels["recommendation"]}</h4>'
        f"<p>{recommendation}</p>"
        "</div>"
    )


def render_message(message):
    """Render one chat message as a custom bubble."""
    # Each message has a role: user or assistant.
    role = message["role"]
    content = message["content"]

    # User messages detect direction from their text.
    # Assistant messages store their direction when created.
    direction = text_direction(content) if role == "user" else message.get("direction", "ltr")

    # CSS classes control bubble color and side alignment.
    bubble_class = "user-bubble" if role == "user" else "assistant-bubble"
    row_class = "user-row" if role == "user" else "assistant-row"

    # Assistant analysis messages are dictionaries, so they are rendered as cards.
    if role == "assistant" and isinstance(content, dict):
        response_language = "ar" if direction == "rtl" else "en"
        body = render_analysis(content, TEXT[response_language], direction, response_language)
    else:
        # Normal text messages are escaped and displayed as plain paragraphs.
        body = f"<p>{html.escape(str(content))}</p>"

    # Streamlit markdown is used to render custom HTML chat bubbles.
    st.markdown(
        (
            f'<div class="chat-row {row_class}">'
            f'<div class="chat-bubble {bubble_class}" dir="{direction}">'
            f"{body}"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def add_user_message(problem):
    """Add a user message to the chat history."""
    st.session_state.messages.append({"role": "user", "content": problem})


def add_assistant_message(content, direction):
    """Add an assistant message to the chat history."""
    st.session_state.messages.append(
        {"role": "assistant", "content": content, "direction": direction}
    )


def submit_problem(problem_text):
    """Handle examples and typed prompts using the same validation and errors."""
    labels = current_labels()
    problem_text = problem_text.strip()

    # Do not call the API if the user sends an empty message.
    if not problem_text:
        st.warning(labels["empty_warning"])
        return

    # Save the user message first so it appears in the conversation.
    add_user_message(problem_text)
    response_direction = text_direction(problem_text)

    try:
        # Show a loading spinner while waiting for the Groq API response.
        with st.spinner(labels["thinking"]):
            analysis = analyze_problem(problem_text)

        # Store the structured AI response as an assistant message.
        add_assistant_message(analysis, response_direction)
    except ValueError:
        # This usually means the API key is missing.
        add_assistant_message(
            f"{labels['missing_key']}\n{labels['missing_key_help']}",
            "rtl" if current_language() == "ar" else "ltr",
        )
    except json.JSONDecodeError:
        # This handles cases where the model returns invalid JSON.
        add_assistant_message(
            labels["format_error"],
            "rtl" if current_language() == "ar" else "ltr",
        )
    except Exception as error:
        # This catches network errors, invalid keys, rate limits, or API failures.
        add_assistant_message(
            f"{labels['api_error']}\n{labels['technical_details']}: {error}",
            "rtl" if current_language() == "ar" else "ltr",
        )

    # Rerun the page so the new message appears immediately.
    st.rerun()


def render_language_switch():
    """Render the English/Arabic language switch."""
    # Streamlit owns the radio state; CSS pins it to the top-right corner.
    st.radio(
        "Language",
        options=["en", "ar"],
        format_func=lambda code: TEXT[code]["language_name"],
        horizontal=True,
        label_visibility="collapsed",
        key="ui_language",
    )


def render_header(page_direction, compact):
    """Render the top navigation bar and page hero section."""
    labels = current_labels()

    # When the conversation starts, the hero becomes smaller to save space.
    hero_class = "hero-copy hero-compact" if compact else "hero-copy"
    description = "" if compact else f"<p>{labels['description']}</p>"

    st.markdown(
        f"""
        <div class="app-nav" dir="{page_direction}">
            <div class="nav-brand">AI Tech Support</div>
            <div class="nav-status">Live Assistant</div>
        </div>
        <div class="{hero_class}" dir="{page_direction}">
            <div class="app-kicker">IT Support Assistant</div>
            <h1>{labels["title"]}</h1>
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_examples():
    """Render example problem buttons on the first screen only."""
    labels = current_labels()

    # Section label above example buttons.
    st.markdown(
        f'<div class="section-title">{labels["examples_title"]}</div>',
        unsafe_allow_html=True,
    )

    # Display examples in two columns for a balanced layout.
    example_columns = st.columns(2)
    for index, example in enumerate(labels["examples"]):
        with example_columns[index % 2]:
            if st.button(example, use_container_width=True):
                # Example buttons behave exactly like typed user prompts.
                submit_problem(example)


def render_clear_button():
    """Render the clear chat button after the conversation starts."""
    labels = current_labels()

    # The button is placed on the right side using columns.
    _, clear_column = st.columns([0.76, 0.24])
    with clear_column:
        if st.button(labels["clear"], use_container_width=True):
            # Remove all messages and return to the start state.
            st.session_state.messages = []
            st.rerun()


def ensure_greeting(page_direction):
    """Add the first assistant greeting when the chat is empty."""
    if not st.session_state.messages:
        add_assistant_message(current_labels()["assistant_greeting"], page_direction)


def render_chat_form():
    """Render the message input form and send button."""
    labels = current_labels()

    # clear_on_submit clears the input after the message is sent.
    with st.form("chat_form", clear_on_submit=True):
        input_column, send_column = st.columns([0.9, 0.1])
        with input_column:
            # Text input sends when the user presses Enter inside the form.
            prompt = st.text_input(
                labels["input_placeholder"],
                label_visibility="collapsed",
                placeholder=labels["input_placeholder"],
            )
        with send_column:
            # Submit button is styled as a send icon through CSS.
            submitted = st.form_submit_button("➤", use_container_width=True)

    if submitted:
        submit_problem(prompt)


def main():
    """Main function that controls the complete Streamlit page."""
    # Prepare session state values before reading or writing them.
    init_session_state()

    # Choose page direction and alignment based on selected UI language.
    language = current_language()
    page_direction = "rtl" if language == "ar" else "ltr"
    align_side = "right" if page_direction == "rtl" else "left"

    # The app changes layout after the user sends the first message.
    conversation_started = has_user_messages()

    # Load custom CSS before rendering visible components.
    load_styles(page_direction, align_side)

    # Render the main interface sections.
    render_language_switch()
    render_header(page_direction, compact=conversation_started)

    # Show examples only before the first real user prompt.
    if conversation_started:
        render_clear_button()
    else:
        render_examples()

    # Add the greeting only if the chat history is empty.
    ensure_greeting(page_direction)

    # Render all previous chat messages in order.
    for message in st.session_state.messages:
        render_message(message)

    # Spacer keeps the form visually separated from the last message.
    st.markdown('<div class="chat-bottom-spacer"></div>', unsafe_allow_html=True)

    # Render the input field at the bottom of the page content.
    render_chat_form()


if __name__ == "__main__":
    # Run the app.
    main()
