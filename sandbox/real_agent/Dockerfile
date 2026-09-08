# Containerized real-agent Dockerfile
# Usage (example):
# docker build -t sebek-real-agent -f sandbox/real_agent/Dockerfile .
# docker run --rm -v /path/to/vosk-model:/models -v /path/to/persist:/data --device /dev/snd sebek-real-agent \
#   --model /models --persist-dir /data --sebek-url http://host.docker.internal:11434/api/observe

FROM python:3.11-slim
WORKDIR /app

# system deps for audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements-speech.txt /app/requirements-speech.txt
RUN pip install --no-cache-dir -r /app/requirements-speech.txt

# install package-native SEBEK module
COPY pyproject.toml setup.py /app/
COPY sebek /app/sebek
RUN pip install --no-cache-dir -e /app

ENTRYPOINT ["/usr/bin/env", "python", "-m", "sebek.speech.agent"]
