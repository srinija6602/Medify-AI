
import streamlit as st
import json
import urllib.request
import urllib.error

# -------------------- PAGE CONFIG --------------------

st.set_page_config(
    page_title="Medify-AI",
    page_icon="🩺",
    layout="wide"
)

# -------------------- PROFESSIONAL UI --------------------

st.markdown("""
<style>
    .stApp {
        background-color: #f4f8fb;
        color: #172b4d;
    }

    [data-testid="stSidebar"] {
        background-color: #102a43;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .main-title {
        color: #087e8b;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #486581;
        font-size: 17px;
        margin-bottom: 22px;
    }

    .info-card {
        background: white;
        border: 1px solid #d9e6ee;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    div.stButton > button[kind="primary"] {
        background-color: #087e8b;
        color: white;
        border: none;
        border-radius: 9px;
        font-weight: 600;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #066873;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- CONSTANTS --------------------

MODEL_NAME = "llama3.2:1b"
API_URL = "http://localhost:11434/api/chat"

HEALTH_WARNING = (
    "Medify-AI provides general health information only. "
    "It cannot diagnose illnesses or replace a qualified healthcare professional."
)

# -------------------- AI FUNCTION --------------------

def ask_ai(messages):
    system_message = {
        "role": "system",
        "content": """
You are Medify-AI, a careful health information assistant.

Always answer in clear, natural English.
Understand the user's question and answer it directly.
Use simple words and useful explanations.
For health questions, explain possible causes without diagnosing.
Give safe, general self-care suggestions when appropriate.
Do not invent facts or claim certainty when the cause is unclear.
Do not prescribe medicines or dosages.
Recommend a qualified healthcare professional when appropriate.
Clearly advise emergency medical care for potentially serious symptoms.
If the question is not about health, answer it helpfully when possible.
Do not expose internal reasoning. Give only the final answer.
"""
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [system_message] + messages,
        "stream": False
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    answer = result.get("message", {}).get("content", "").strip()

    if not answer:
        raise ValueError("The AI returned an empty answer.")

    return answer

# -------------------- EMERGENCY CHECK --------------------

def urgent_symptom(symptoms):
    urgent = {"Chest pain", "Breathing difficulty"}

    return any(symptom in urgent for symptom in symptoms)

# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown("## 🩺 Medify-AI")
    st.caption("Your AI Health Information Assistant")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Home", "Symptom Checker", "AI Chatbot"]
    )

    st.markdown("---")
    st.info(HEALTH_WARNING)

# -------------------- HOME PAGE --------------------

if page == "Home":
    st.markdown(
        '<p class="main-title">🩺 Medify-AI</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Your AI Health Information Assistant</p>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
        <h3>Welcome to Medify-AI</h3>
        <p>
        Explore general health information, learn about common symptoms,
        and ask health-related questions using the AI chatbot.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🔍 Symptom Checker</h3>
            <p>
            Explore possible explanations for common symptoms
            and learn when to seek medical care.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Symptom Checker", type="primary",
                     use_container_width=True):
            st.session_state.current_page = "Symptom Checker"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🤖 AI Health Chatbot</h3>
            <p>
            Ask questions about health, common conditions,
            prevention, and general wellness.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open AI Chatbot", type="primary",
                     use_container_width=True):
            st.session_state.current_page = "AI Chatbot"
            st.rerun()

    st.warning(HEALTH_WARNING)

# -------------------- SYMPTOM CHECKER --------------------

elif page == "Symptom Checker":
    st.markdown(
        '<p class="main-title">🔍 Symptom Checker</p>',
        unsafe_allow_html=True
    )

    st.write(
        "Select your symptoms to receive general health information."
    )

    symptoms = st.multiselect(
        "Select your symptoms",
        [
            "Headache",
            "Fever",
            "Cough",
            "Cold",
            "Sore throat",
            "Nausea",
            "Stomach pain",
            "Fatigue",
            "Dizziness",
            "Vomiting",
            "Diarrhea",
            "Body pain",
            "Breathing difficulty",
            "Chest pain"
        ]
    )

    duration = st.selectbox(
        "How long have you had these symptoms?",
        [
            "Less than one day",
            "1–3 days",
            "4–7 days",
            "More than one week"
        ]
    )

    details = st.text_area(
        "Additional details (optional)",
        placeholder="Describe your symptoms, severity, or other relevant details."
    )

    if st.button("Get Health Information", type="primary"):
        if not symptoms:
            st.warning("Please select at least one symptom.")

        elif urgent_symptom(symptoms):
            st.error(
                "Chest pain or difficulty breathing can be serious. "
                "Seek urgent medical care now. Do not wait for an AI response."
            )

        else:
            prompt = f"""
Explain the following symptoms in clear, simple English.

Symptoms: {", ".join(symptoms)}
Duration: {duration}
Additional details: {details or "Not provided"}

Include:
1. Common possible causes, without diagnosing.
2. Safe self-care suggestions when appropriate.
3. Warning signs that require medical attention.
4. When to consult a healthcare professional.

Do not prescribe medicines.
Do not assume the symptoms are harmless.
"""

            with st.spinner("Preparing your health information..."):
                try:
                    answer = ask_ai([
                        {"role": "user", "content": prompt}
                    ])

                    st.markdown("### 🩺 Health Information")
                    st.markdown(answer)
                    st.warning(HEALTH_WARNING)

                except Exception:
                    st.error(
                        "Unable to get an AI response. "
                        "Check that the AI service is running and try again."
                    )

# -------------------- AI CHATBOT --------------------

elif page == "AI Chatbot":
    st.markdown(
        '<p class="main-title">🤖 AI Health Chatbot</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Ask your health questions in English.</p>',
        unsafe_allow_html=True
    )

    st.info(HEALTH_WARNING)

    if "medify_messages" not in st.session_state:
        st.session_state.medify_messages = []

    for message in st.session_state.medify_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Type your health question here...")

    if question:
        st.session_state.medify_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Preparing your answer..."):
                try:
                    # Keep recent conversation context.
                    history = st.session_state.medify_messages[-12:]

                    answer = ask_ai(history)

                    st.markdown(answer)

                    st.session_state.medify_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                except urllib.error.URLError:
                    st.error(
                        "Could not connect to the AI service. "
                        "Please make sure the AI service is running."
                    )

                except Exception:
                    st.error(
                        "Something went wrong while preparing the answer. "
                        "Please try again."
                    )

    if st.session_state.medify_messages:
        if st.button("Clear Chat"):
            st.session_state.medify_messages = []
            st.rerun()
