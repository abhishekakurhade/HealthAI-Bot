# Lightweight Python image
FROM python:3.10-slim

# Workdir
WORKDIR /app

# Do not write .pyc, use unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=1

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Streamlit settings
ENV STREAMLIT_SERVER_HEADLESS=true     STREAMLIT_SERVER_PORT=8501     STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "Healthai.py", "--server.address=0.0.0.0", "--server.port=8501"]
