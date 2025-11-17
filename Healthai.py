import os
import requests
import streamlit as st
import speech_recognition as sr
import pyaudio

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
# Custom CSS (Dark Theme)
# -------------------------
CUSTOM_CSS = """
<style>
body {
  background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
  color: #fff;
  font-family: 'Poppins', sans-serif;
}
.stTextInput input {
  background: rgba(255,255,255,0.1);
  color: white !important;
  border-radius: 12px !important;
  border: 1px solid #00c6ff !important;
}
.mic-btn {
  background: linear-gradient(135deg, #00c6ff, #0072ff);
  color: white;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  font-size: 22px;
  cursor: pointer;
  transition: 0.3s;
}
.mic-btn:active {
  background: linear-gradient(135deg, #ff512f, #dd2476);
}
.healthai-disclaimer {
  position: fixed;
  bottom: 6px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 13px;
  padding: 8px 14px;
  background: rgba(0,0,0,0.5);
  border-radius: 8px;
  color: #ff6b6b;
  font-weight: bold;
  z-index: 1000;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------
# API Setup
# -------------------------
def _get_secret_key():
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return os.getenv("OPENROUTER_API_KEY", "")

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

def call_openrouter(messages, language, temperature: float = 0.3, max_tokens: int = 500):
    """
    Sends chat messages to the OpenRouter API and ensures language context.
    """
    api_key = _get_secret_key()
    if not api_key:
        return "⚠️ No API key found. Please set it in environment variables or Streamlit secrets."

    # System prompt to ensure language control
    system_prompt = {
        "role": "system",
        "content": (
            f"You are HealthAI, a helpful health assistant. "
            f"Always respond in {language}. "
            "⚠️ Only answer health-related questions. "
            "If the question is unrelated to health, reply: "
            "'I can only help with health-related guidance.' "
            "Response format:\n"
            "1) Overview\n2) Home care\n3) Safe OTC medicines\n4) Ayurvedic options\n5) When to see a doctor."
        ),
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [system_prompt] + messages[-10:],  # Keep last 10 messages
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        return f"⚠️ Error {resp.status_code}: {resp.text}"
    return resp.json()["choices"][0]["message"]["content"].strip()

# -------------------------
# Session State Init
# -------------------------
if "_lang" not in st.session_state:
    st.session_state["_lang"] = "English"
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi, I’m HealthAI. How can I assist you today?"}
    ]
if "mic_status" not in st.session_state:
    st.session_state["mic_status"] = "🎤 Mic Ready"
if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

# -------------------------
# Language Mapping for STT
# -------------------------
LANGUAGE_CODES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Tamil": "ta-IN"
}

# -------------------------
# Mic Device Checker
# -------------------------
def check_microphone_device():
    try:
        p = pyaudio.PyAudio()
        devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                devices.append((i, info["name"]))
        p.terminate()
        if not devices:
            return False, "No active microphone devices found. Check audio input or permissions."
        return True, devices
    except Exception as e:
        return False, f"Mic device error: {e}"

# -------------------------
# Voice Recognition (Multilingual)
# -------------------------
def recognize_speech_once():
    recognizer = sr.Recognizer()
    ok, devices = check_microphone_device()
    if not ok:
        st.session_state["mic_status"] = f"❌ {devices}"
        return ""

    language_code = LANGUAGE_CODES.get(st.session_state["_lang"], "en-IN")

    try:
        with sr.Microphone() as source:
            st.session_state["mic_status"] = f"🎙 Listening in {st.session_state['_lang']}..."
            st.toast(f"🎧 Speak in {st.session_state['_lang']}...", icon="🎤")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=6)
            st.session_state["mic_status"] = "🧠 Processing..."
            text = recognizer.recognize_google(audio, language=language_code)
            st.session_state["input_text"] = text
            st.session_state["mic_status"] = f"✅ Recognized: {text}"
            return text
    except sr.UnknownValueError:
        st.session_state["mic_status"] = f"⚠️ Could not understand {st.session_state['_lang']} speech."
    except sr.WaitTimeoutError:
        st.session_state["mic_status"] = "⏱️ No speech detected."
    except sr.RequestError:
        st.session_state["mic_status"] = "❌ Speech API unavailable."
    except Exception as e:
        st.session_state["mic_status"] = f"❌ Mic error: {type(e).__name__}: {e}"
    return ""

# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    prev_lang = st.session_state["_lang"]
    st.session_state["_lang"] = st.selectbox(
        "Response Language", list(LANGUAGE_CODES.keys()), index=list(LANGUAGE_CODES.keys()).index(prev_lang)
    )

    if st.session_state["_lang"] != prev_lang:
        st.toast(f"🌐 Language changed to {st.session_state['_lang']}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Language switched to {st.session_state['_lang']}. Speak or type in this language now."
        })

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": f"🩺 Chat cleared. Let's start fresh in {st.session_state['_lang']}!"}
        ]
        st.session_state["input_text"] = ""

# -------------------------
# Chat Messages Display
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# Input Field + Mic
# -------------------------
col1, col2 = st.columns([6, 1])
with col1:
    prompt = st.text_input(
        f"Ask your question in {st.session_state['_lang']}...",
        value=st.session_state["input_text"],
        key="chat_input",
        placeholder=f"Type or speak in {st.session_state['_lang']}..."
    )

with col2:
    if st.button("🎙"):
        recognize_speech_once()
        st.rerun()

st.caption(st.session_state["mic_status"])

# -------------------------
# Chat Response
# -------------------------
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner(f"Analyzing and replying in {st.session_state['_lang']}..."):
            reply = call_openrouter(st.session_state.messages, st.session_state["_lang"], temperature=0.3)
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state["input_text"] = ""  # reset after sending

# -------------------------
# Footer
# -------------------------
st.markdown("<div class='healthai-disclaimer'>⚠️ This bot is not a substitute for medical advice.</div>", unsafe_allow_html=True)
