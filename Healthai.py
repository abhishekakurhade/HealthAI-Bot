import os
import requests
import streamlit as st
import speech_recognition as sr

# -------------------------
# App Config
# -------------------------
st.set_page_config(
    page_title="HealthAI Chatbot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------
# Custom CSS
# -------------------------
CUSTOM_CSS = """
<style>
@keyframes heartbeat {
  0% { transform: scale(1); color: #22d3ee; }
  25% { transform: scale(1.2); color: #8b5cf6; }
  50% { transform: scale(1); color: #22d3ee; }
  75% { transform: scale(1.2); color: #8b5cf6; }
  100% { transform: scale(1); color: #22d3ee; }
}
.heartbeat { font-size: 22px; animation: heartbeat 1s infinite; }

.healthai-disclaimer {
  position: fixed; bottom: 4px; left: 50%; transform: translateX(-50%);
  font-size: 13px; padding: 6px 12px;
  background: rgba(0,0,0,0.6); border-radius: 8px;
  color: #ff6b6b; font-weight: bold;
  z-index: 1000;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------
# API Setup
# -------------------------
def _get_secret_key():
    if "__openrouter_key" in st.session_state and st.session_state["__openrouter_key"]:
        return st.session_state["__openrouter_key"]
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return os.getenv("OPENROUTER_API_KEY", "")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

def call_openrouter(messages, temperature: float = 0.3, max_tokens: int = 500):
    api_key = _get_secret_key()
    if not api_key:
        return "⚠️ No API key found. Set it in Settings."
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        return f"⚠️ OpenRouter error {resp.status_code}: {resp.text}"
    return resp.json()["choices"][0]["message"]["content"].strip()

# -------------------------
# Prompts
# -------------------------
BASE_PROMPT = (
    "You are HealthAI, a helpful health assistant. "
    "⚠️ IMPORTANT: Only answer health-related questions. "
    "❌ If non-health, reply: 'I can only help with health-related guidance.' "
    "Always reply in {lang}. "
    "Response format: \n"
    "1) Short overview\n2) Home care\n3) Safe OTC medicines\n4) Ayurvedic options\n5) When to see a doctor.\n"
    "Supportive tone, no diagnosis, not a substitute for professional care."
)

# -------------------------
# Session State
# -------------------------
if "_temp" not in st.session_state:
    st.session_state["_temp"] = 0.3
if "_lang" not in st.session_state:
    st.session_state["_lang"] = "English"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": BASE_PROMPT.format(lang=st.session_state["_lang"])},
        {"role": "assistant", "content": "👋 Hi, I’m your Health Assistant. How can I help you today?"}
    ]
if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state["_lang"] = st.selectbox(
        "Response Language",
        ["English", "Hindi", "Marathi", "Gujarati", "Rajasthani"],
        index=["English","Hindi","Marathi","Gujarati","Rajasthani"].index(st.session_state["_lang"])
    )

    st.markdown("### 📜 Chat History")
    if st.session_state.history:
        for i, old_chat in enumerate(st.session_state.history):
            if st.button(f"Chat {i+1}"):
                st.session_state.messages = old_chat.copy()
                st.rerun()

    st.markdown("---")
    if st.button("🗑 Clear Current Chat"):
        st.session_state.history.append(st.session_state.messages.copy())
        st.session_state.messages = [
            {"role": "system", "content": BASE_PROMPT.format(lang=st.session_state["_lang"])},
            {"role": "assistant", "content": "👋 New chat started. How can I help you?"}
        ]
        st.rerun()

# -------------------------
# Mic Input Button
# -------------------------
st.markdown("### 🎤 Speak your health question")
if st.button("🎙 Tap to Speak"):
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎧 Listening... Please speak now.")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"🗣 You said: {text}")
            st.session_state.messages.append({"role": "user", "content": text})
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    st.session_state.messages[0]["content"] = BASE_PROMPT.format(lang=st.session_state["_lang"])
                    reply = call_openrouter(st.session_state.messages[-10:], temperature=st.session_state["_temp"])
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
    except AttributeError:
        st.error("⚠️ PyAudio not found. Please install it using:\n\n`pip install pipwin && pipwin install pyaudio`")
    except sr.WaitTimeoutError:
        st.warning("⏱️ Listening timed out. Please try again.")
    except Exception as e:
        st.error(f"🎙️ Error: {e}")

# -------------------------
# Chat Screen
# -------------------------
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message("assistant" if msg["role"] == "assistant" else "user"):
        st.markdown(msg["content"])

# -------------------------
# Text Input
# -------------------------
if prompt := st.chat_input("Ask about a symptom or disease..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            st.markdown("<div class='heartbeat'>🔵🔴</div>", unsafe_allow_html=True)
            st.session_state.messages[0]["content"] = BASE_PROMPT.format(lang=st.session_state["_lang"])
            reply = call_openrouter(st.session_state.messages[-10:], temperature=st.session_state["_temp"])
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# -------------------------
# Info Cards
# -------------------------
if st.checkbox("📊 Show Info Cards (Diet/Exercise/Symptoms)"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🥗 Diet Tips")
        st.write("- Eat fresh fruits\n- Drink 2-3L water\n- Avoid junk food")
    with col2:
        st.subheader("🏃 Exercise")
        st.write("- 30 min walk daily\n- Light yoga\n- Breathing exercises")
    with col3:
        st.subheader("🤒 Symptoms Summary")
        st.write("- Common cold: runny nose, mild fever\n- Dengue: high fever, body pain")

# -------------------------
# Footer
# -------------------------
st.markdown("<div class='healthai-disclaimer'>⚠️ This bot is not a substitute for a doctor.</div>", unsafe_allow_html=True)
