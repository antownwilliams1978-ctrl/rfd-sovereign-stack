SEBEK Speech Agent (Vosk) - README

This directory adds a multiprocess speech agent that captures microphone audio, runs offline ASR with Vosk, and posts final transcripts to SEBEK at http://localhost:11434/api/observe

Quick install (automated):

1) Clone the repo into /opt and run the setup script as root (the script will create a system user, virtualenv, install requirements, install SEBEK in editable mode, download a Vosk model, set permissions, and install the systemd unit):

   sudo git clone https://github.com/rfd-core/rfd-sovereign-stack.git /opt/rfd-sovereign-stack
   sudo /opt/rfd-sovereign-stack/setup/sebek_setup.sh

2) Manual steps (if you prefer to run manually):
   sudo apt update
   sudo apt install -y python3-venv python3-pip build-essential libsndfile1 ffmpeg unzip wget

   # Create venv and install
   python3 -m venv /opt/sebek-speech-venv
   source /opt/sebek-speech-venv/bin/activate
   pip install -r /opt/rfd-sovereign-stack/requirements-speech.txt

   # Download the Vosk model
   sudo mkdir -p /opt/vosk-models
   cd /opt/vosk-models
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   sudo mv vosk-model-small-en-us-0.15 /opt/vosk-model-small-en-us-0.15

   # Create persist dir
   sudo mkdir -p /var/lib/sebek/speech
   sudo chown sebek:sebek /var/lib/sebek/speech

   # Install systemd unit (ensure User=sebek in the unit file)
   sudo cp /opt/rfd-sovereign-stack/sebek-speech.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable sebek-speech
   sudo systemctl start sebek-speech

Speech agent launch:
   source /opt/sebek-speech-venv/bin/activate
   python -m sebek.speech.agent --model /opt/vosk-model-small-en-us-0.15 --persist-dir /var/lib/sebek/speech

Notes & Troubleshooting:
- The setup script assumes the repository is cloned to /opt/rfd-sovereign-stack. If you cloned elsewhere, adjust paths accordingly.
- Microphone access: services running as a system user may need audio group membership or ALSA device configuration. If the service cannot access the microphone under systemd, run the agent manually as your user to debug and then adapt the service.
- SEBEK endpoint: the agent posts JSON payloads to /api/observe. Adjust --sebek-url if your SEBEK engine listens on a different path/port.
- For improved accuracy, replace the Vosk model with a larger model or switch to a higher-quality ASR backend when you have GPU resources.
