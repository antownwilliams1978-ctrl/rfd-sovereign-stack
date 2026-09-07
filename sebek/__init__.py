"""SEBEK: Sovereign Local Intelligence Engine for the Red Feather Dynasty.

A unified digital operating environment (DSOS) combining:
- Headless e-commerce platform
- Local LLM inference (Ollama)
- Voice-driven system control (Vosk ASR + pyttsx3 TTS)
- Semantic knowledge retrieval (LangChain + Chroma)
"""

__version__ = "0.1.0"
__author__ = "Red Feather Dynasty"
__license__ = "MIT"

# Import key components for convenient access
from sebek.config import Config
from sebek.utils.logging import get_logger

__all__ = [
    "Config",
    "get_logger",
    "__version__",
    "__author__",
    "__license__",
]
