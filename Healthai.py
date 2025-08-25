import os
import requests
import streamlit as st

# -------------------------
# App Config
# -------------------------
st.set_page_config(
    page_title="HealthAI Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"  # keep hidden by default (esp. on mobile)
)

# -------------------------
# Custom CSS (Dark + Responsive + Mobile Toggle styling)
# -------------------------
CUSTOM_CSS = """
<style>
:root {
  --bg: #0b0f14;
  --panel: #0f1620;
  --text: #e6eef8;
  --muted: #98a2b3;
  --accent: #22d3ee;
  --accent-2: #8b5cf6;
}
html, body, [data-testid="stApp"] {
  background: radial-gradient(1200px 800px at 20% -10%, rgba(34,211,238,0.08), transparent 60%),
              radial-gradient(1000px 700px at 120% 10%, rgba(139,92,246,0.07), transparent 60%),
              var(--bg) !important;
  color: var(--text) !important;
}

/* Brand + Footer */
.healthai-brand {
  position: fixed; top: 14px; right: 18px;
  font-weight: 800; font-size: 16px; color: var(--text);
  padding: 8px 12px; border-radius: 999px;
  background: linear-gradient(135deg, rgba(34,211,238,0.18), rgba(139,92,246,0.18));
  border: 1px solid rgba(255,255,255,0.08);
  z-index: 1000;
}
.healthai-footer {
  position: fixed; bottom: 8px; left: 50%; transform: translateX(-50%);
  color: var(--muted); font-size: 13px;
  background: rgba(15,22,32,0.6); backdrop-filter: blur(8px);
  padding: 6px 12px; border-radius: 12px;
  z-index: 900;
}

/* Chat */
.chat-wrap { width: min(900px, 95vw); margin: 0 auto; padding: 16px 0 100px 0; }
.chat-panel { border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; padding: 14px; background: var(--panel); }
.msg { border-radius: 16px; padding: 12px 14px; margin: 8px 0; line-height: 1.5; }
.msg.user { background: rgba(34,211,238,0.08); text-align: right; }
.msg.assistant { background: rgba(139,92,246,0.09); text-align: left; }
.msg.system { background: rgba(255,255,255,0.04); color: var(--muted); font-style: italic; }

/* Input */
.input-bar { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%);
  width: min(900px, 95vw); z-index: 950; }
.input-inner { display: grid; grid-template-columns: 1fr auto; gap: 8px;
  background: var(--panel); padding: 10px; border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.input-inner textarea {
  resize: none; min-height: 50px; max-height: 120px;
  border-radius: 12px !important;
  background: rgba(255,255,255,0.05); color: var(--text);
}
.send-btn { height: 50px; padding: 0 18px; border-radius: 12px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #071018; font-weight: 700; border: none; }

/* IMPORTANT: keep header visible so the real sidebar toggle works */
footer { visibility: hidden; }          /* ok to hide footer */
header { visibility: visible !important; }  /* DO NOT hide header */

/* Make Streamlit's own sidebar toggle a floating gear on mobile */
@media (max-width: 768px) {
  /* style the built-in toggle buttons */
  button[title="Show sidebar"], button[title="Hide sidebar"] {
    position: fixed !important;
    top: 16px !important;
    left: 16px !important;
    z-index: 2000 !important;
    width: 46px !important;
    height: 46px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #22d3ee, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
  }
  /* Hide the default inner icon/text and show a gear */
  button[title="Show sidebar"] > *, button[title="Hide sidebar"] > * {
    opacity: 0 !important;
  }
  button[title="Show sidebar"]::after, button[title="Hide sidebar"]::after {
    content: "⚙️";
    font-size: 22px;
    position: absolute; inset: 0;
    display: grid; place-items: center;
  }

  /* Chat padding a bit larger on phones */
  .chat-wrap { padding-bottom: 120px; }
  .input-inner textarea { min-height: 44px; }
  .send-btn { height: 44px; }
}

/* Optional: nicer sidebar width on all screens */
section[data-testid="stSidebar"] {
  min-width: 280px !important;
  max-width: 320px !important;
}
</style>
<div class="healthai-brand">HealthAI</div>
<div class="healthai-footer"><b>To keep the body in good health is a duty… ❤️</b></div>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -------------------------
# API Setup (with in-app key override)
# -------------------------
def _get_secret_key():
    # priority: sidebar input (session) -> Streamlit secrets -> env var
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
        "HTTP-Referer": "https://streamlit.io/",
        "X-Title": "HealthAI Chatbot",
    }
    resp = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        return f"⚠️ OpenRouter error {resp.status_code}: {resp.text}"
    return resp.json()["choices"][0]["message"]["content"].strip()

# -------------------------
# System Prompt
# -------------------------
BASE_PROMPT = (
    "You are HealthAI, a helpful health assistant. "
    "⚠️ IMPORTANT: Only answer health-related questions. "
    "❌ If non-health, reply: 'I can only help with health-related guidance.' "
    "Always reply in {lang}. "
    "Response format: \\n"
    "1) Short overview\\n2) Home care\\n3) Safe OTC medicines\\n4) Ayurvedic options\\n5) When to see a doctor.\\n"
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
        {"role": "assistant", "content": "Hi 👋 I'm HealthAI. Tell me a disease or symptom, and I'll share remedies and guidance. (Not medical advice)."}
    ]

# -------------------------
# Sidebar (real, opens via the styled built-in toggle)
# -------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state["_temp"] = st.slider("Creativity", 0.0, 1.0, st.session_state["_temp"], 0.05)
    st.session_state["_lang"] = st.selectbox(
        "Response Language",
        ["English", "Hindi", "Marathi", "Gujarati", "Rajasthani"],
        index=["English","Hindi","Marathi","Gujarati","Rajasthani"].index(st.session_state["_lang"])
    )

    

    # Key status
    if _get_secret_key():
        st.success("API key is set.")
    else:
        st.warning("API key missing. Add it above.")

    st.markdown("---")
    st.caption("Model:OpenAI GPT-3.5-turbo")

# -------------------------
# Chat UI
# -------------------------
st.markdown("<div class='chat-wrap'><div class='chat-panel'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    css_class = "assistant" if msg["role"] == "assistant" else "user"
    st.markdown(f"<div class='msg {css_class}'>{msg['content']}</div>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# -------------------------
# Input Handling
# -------------------------
def submit_message():
    user_input = st.session_state._user_input.strip()
    if not user_input:
        return
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking…"):
        # ensure language is always respected
        st.session_state.messages[0]["content"] = BASE_PROMPT.format(lang=st.session_state["_lang"])
        reply = call_openrouter(st.session_state.messages[-10:], temperature=st.session_state["_temp"])

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state._user_input = ""
    st.rerun()

st.markdown("<div class='input-bar'><div class='input-inner'>", unsafe_allow_html=True)
st.text_area("Your message", key="_user_input",
             placeholder="Ask about a symptom or disease (e.g., 'What helps for dengue recovery?')",
             label_visibility="collapsed", height=56, on_change=submit_message)
st.button("Send", key="send_btn", on_click=submit_message, use_container_width=True)
st.markdown("</div></div>", unsafe_allow_html=True)
