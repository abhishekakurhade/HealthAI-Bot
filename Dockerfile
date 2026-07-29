FROM python:3.10-slim

WORKDIR /healthbot


COPY requirements.txt /healthbot/requirements.txt
RUN apt-get update  && apt-get install -y \
    build-essential \
    libsndfile1 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY Healthai.py /healthbot/Healthai.py
COPY voice.py   /healthbot/voice.py
COPY chat_history.json /healthbot/chat_history.json


EXPOSE 8501

CMD ["streamlit", "run", "Healthai.py"]



