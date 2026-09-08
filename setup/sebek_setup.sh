#!/usr/bin/env bash
set -euo pipefail

# sebek_setup.sh - Automated setup for SEBEK Speech Agent (Vosk)
# Run as root or with sudo.

SEBEK_USER=sebek
REPO_DIR=/opt/rfd-sovereign-stack
VENV_DIR=/opt/sebek-speech-venv
MODEL_DIR=/opt/vosk-model-small-en-us-0.15
PERSIST_DIR=/var/lib/sebek/speech
SERVICE_FILE=/etc/systemd/system/sebek-speech.service
REQ_FILE=${REPO_DIR}/requirements-speech.txt

echo "== SEBEK Speech Agent Setup =="

# 1) Create system user
if ! id -u "$SEBEK_USER" >/dev/null 2>&1; then
  echo "Creating user $SEBEK_USER"
  useradd -r -m -s /usr/sbin/nologin "$SEBEK_USER"
else
  echo "User $SEBEK_USER already exists"
fi

# Add to audio group if available
if getent group audio >/dev/null 2>&1; then
  usermod -aG audio "$SEBEK_USER" || true
  echo "Added $SEBEK_USER to audio group"
fi

# 2) Ensure repo is in place (assumes you've pushed/copy repo to ${REPO_DIR})
if [ ! -d "$REPO_DIR" ]; then
  echo "Please clone this repository to $REPO_DIR before running the script. Exiting."
  echo "Example: sudo git clone https://github.com/rfd-core/rfd-sovereign-stack.git $REPO_DIR"
  exit 1
fi

# 3) Create venv and install Python deps
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
if [ -f "$REQ_FILE" ]; then
  pip install -r "$REQ_FILE"
else
  echo "Requirements file not found at $REQ_FILE; please ensure it's present."
fi
pip install -e "$REPO_DIR"

# 4) Download Vosk model if not present
if [ ! -d "$MODEL_DIR" ]; then
  echo "Downloading Vosk small English model to $MODEL_DIR"
  mkdir -p /opt/vosk-models
  cd /opt/vosk-models
  # model URL may change; user should verify
  wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
  unzip vosk-model-small-en-us-0.15.zip
  mv vosk-model-small-en-us-0.15 "$MODEL_DIR"
  rm -f vosk-model-small-en-us-0.15.zip
fi

# 5) Create persist directory and set permissions
mkdir -p "$PERSIST_DIR"
chown -R "$SEBEK_USER":"$SEBEK_USER" "$PERSIST_DIR"
chmod 750 "$PERSIST_DIR"

# 6) Install systemd unit (overwrite if present)
if [ -f "$REPO_DIR/sebek-speech.service" ]; then
  cp "$REPO_DIR/sebek-speech.service" "$SERVICE_FILE"
  chown root:root "$SERVICE_FILE"
  chmod 644 "$SERVICE_FILE"
  echo "Installed systemd unit to $SERVICE_FILE"
else
  echo "Unit file not found in repo: $REPO_DIR/sebek-speech.service"
fi

# 7) Ensure working dir permissions
chown -R "$SEBEK_USER":"$SEBEK_USER" "$REPO_DIR"

# 8) Reload systemd and enable service
systemctl daemon-reload
systemctl enable sebek-speech
systemctl start sebek-speech

# 9) Print status
systemctl status sebek-speech --no-pager || true

echo "Setup complete. If the service failed to start, check journalctl -u sebek-speech -f"
