"""Speech recognition and synthesis for SEBEK.

Handles offline ASR (Vosk) and text-to-speech (pyttsx3) operations.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import time
import uuid
from dataclasses import dataclass

try:
    from vosk import Model, KaldiRecognizer
    HAS_VOSK = True
except ImportError:
    HAS_VOSK = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

import wave
from sebek.config import Config
from sebek.utils.errors import SpeechError

logger = logging.getLogger(__name__)


@dataclass
class SpeechRecognitionResult:
    """Result of speech recognition operation."""

    text: str
    """Recognized text."""

    confidence: Optional[float] = None
    """Confidence score (0-1), if available."""

    words: Optional[List[Dict[str, Any]]] = None
    """Word-level details with timing and confidence."""

    vosk_result: Optional[Dict[str, Any]] = None
    """Raw Vosk JSON result."""

    audio_path: Optional[Path] = None
    """Path to persisted audio snippet."""

    timestamp: Optional[str] = None
    """Timestamp of recognition (YYYYMMDD_HHMMSS)."""


class VoskRecognizer:
    """Wrapper for Vosk offline speech recognition.

    Provides a simplified interface to Vosk for ASR without cloud dependency.

    Attributes:
        model_path (Path): Path to Vosk model directory.
        model (Model): Loaded Vosk model.
        recognizer (KaldiRecognizer): Vosk recognizer instance.
    """

    def __init__(self, model_path: Optional[Path] = None):
        """Initialize Vosk recognizer.

        Args:
            model_path: Path to Vosk model. Uses config default if None.

        Raises:
            SpeechError: If Vosk is unavailable or model not found.
        """
        if not HAS_VOSK:
            raise SpeechError("Vosk is not installed")

        self.model_path = model_path or Config.speech.vosk_model_path

        if not self.model_path.exists():
            raise SpeechError(f"Vosk model not found at: {self.model_path}")

        try:
            self.model = Model(str(self.model_path))
            self.recognizer = KaldiRecognizer(self.model, Config.speech.sample_rate)
            self.recognizer.SetWords(True)  # Enable word-level details
            logger.info(f"Vosk recognizer initialized with model: {self.model_path}")
        except Exception as e:
            raise SpeechError(f"Failed to initialize Vosk: {e}") from e

    def accept_waveform(self, audio_bytes: bytes) -> bool:
        """Feed audio bytes to recognizer and check for result.

        Args:
            audio_bytes: Raw audio data (int16 PCM).

        Returns:
            bool: True if a final result is ready, False if still listening.

        Raises:
            SpeechError: If audio processing fails.
        """
        try:
            return self.recognizer.AcceptWaveform(audio_bytes)
        except Exception as e:
            raise SpeechError(f"Audio processing failed: {e}") from e

    def get_result(self) -> SpeechRecognitionResult:
        """Get final recognition result.

        Returns:
            SpeechRecognitionResult: Recognized text and metadata.

        Raises:
            SpeechError: If result parsing fails.
        """
        try:
            result_json = json.loads(self.recognizer.Result())
        except Exception as e:
            raise SpeechError(f"Failed to parse recognition result: {e}") from e

        text = result_json.get("text", "").strip()
        words = result_json.get("result", [])

        # Calculate average confidence
        confidences = [
            w.get("conf")
            for w in words
            if isinstance(w.get("conf"), (int, float))
        ]
        avg_confidence = float(sum(confidences) / len(confidences)) if confidences else None

        return SpeechRecognitionResult(
            text=text,
            confidence=avg_confidence,
            words=words,
            vosk_result=result_json,
            timestamp=time.strftime("%Y%m%d_%H%M%S"),
        )

    def get_partial_result(self) -> str:
        """Get partial recognition result (still listening).

        Returns:
            str: Partial text recognized so far.
        """
        try:
            partial_json = json.loads(self.recognizer.PartialResult())
            return partial_json.get("partial", "")
        except Exception:
            return ""

    def reset(self) -> None:
        """Reset recognizer state for next utterance."""
        try:
            # Recreate recognizer to clear state
            self.recognizer = KaldiRecognizer(self.model, Config.speech.sample_rate)
            self.recognizer.SetWords(True)
        except Exception as e:
            logger.error(f"Failed to reset recognizer: {e}")


class TextToSpeech:
    """Wrapper for text-to-speech synthesis.

    Provides offline TTS using pyttsx3.
    """

    def __init__(self, enable: bool = True):
        """Initialize text-to-speech engine.

        Args:
            enable: Whether to enable TTS. If False, speak() is a no-op.
        """
        self.enabled = enable and HAS_TTS
        self.engine = None

        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                logger.info("Text-to-speech engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize TTS: {e}")
                self.enabled = False

    def speak(self, text: str) -> None:
        """Synthesize and play audio for text.

        Args:
            text: Text to speak.
        """
        if not self.enabled or not self.engine:
            return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.warning(f"TTS failed for '{text}': {e}")

    def is_available(self) -> bool:
        """Check if TTS is available and working.

        Returns:
            bool: True if TTS is ready to use.
        """
        return self.enabled and self.engine is not None


def save_audio_to_wav(
    path: Path,
    audio_bytes: bytes,
    sample_rate: int = Config.speech.sample_rate,
    channels: int = Config.speech.channels,
) -> None:
    """Save raw audio bytes to WAV file.

    Args:
        path: Output file path.
        audio_bytes: Raw int16 PCM audio data.
        sample_rate: Sample rate in Hz. Defaults to config.
        channels: Number of channels. Defaults to config.

    Raises:
        SpeechError: If file write fails.
    """
    try:
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_bytes)
        logger.debug(f"Saved audio to {path}")
    except (IOError, OSError) as e:
        raise SpeechError(f"Failed to save audio to {path}: {e}") from e
