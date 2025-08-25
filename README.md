# HealthAI Chatbot (Streamlit)

A sleek, dark-themed health assistant chatbot built with **Streamlit**. It calls the **OpenRouter** Chat Completions API and supports **multiple languages** (English, Hindi, Marathi, Gujarati, Rajasthani). The sidebar is fixed open (static) and exposes controls for **temperature** and **language**.

> ⚠️ This app provides general wellness information and is **not a substitute for professional medical advice**.

---

## Features
- 🩺 Short, practical guidance on common symptoms/conditions
- 🌿 Includes Ayurvedic options (with cautions)
- 🌍 Multilingual answers (English/Hindi/Marathi/Gujarati/Rajasthani)
- 🎛️ Static sidebar (temperature + language)
- 🔒 API key stored safely in `secrets.toml` (or environment variable)

---

## 1) Local Setup

### Prerequisites
- Python 3.9–3.11
- A terminal (Command Prompt / PowerShell / bash)

### Clone / Copy your project
Put your `Healthai.py` in the project root, e.g.
```
health-bot/
├─ Healthai.py
└─ .streamlit/
   └─ secrets.toml
```

### Create virtual environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure secrets
Create a file at **`.streamlit/secrets.toml`**:

```toml
OPENROUTER_API_KEY = "sk-or-v1-REPLACE_WITH_YOUR_REAL_KEY"
```

> Alternatively, you can set an environment variable:
> - Windows (PowerShell): `setx OPENROUTER_API_KEY "sk-or-v1-..."`
> - macOS/Linux (bash): `export OPENROUTER_API_KEY="sk-or-v1-..."`

### Run the app
```bash
streamlit run Healthai.py
```
Open the URL shown in the terminal (usually http://localhost:8501).

---

## 2) Docker

### Build
```bash
docker build -t healthai-chatbot .
```

### Run (with secrets)
The easiest way is to **mount** a local `.streamlit` directory that contains your `secrets.toml`:
```bash
docker run --rm -p 8501:8501   -v ${PWD}/.streamlit:/app/.streamlit   --name healthai healthai-chatbot
```
> On Windows PowerShell, use `${PWD}`. On cmd.exe, use `%cd%`.

Now open: http://localhost:8501

#### .dockerignore (optional but recommended)
Create a `.dockerignore` file to keep the image small:
```
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
.streamlit/secrets.toml
```

---





