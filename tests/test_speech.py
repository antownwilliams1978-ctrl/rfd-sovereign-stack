"""Tests for SEBEK speech recognition module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from sebek.speech.recognizer import (
    VoskRecognizer,
    TextToSpeech,
    save_audio_to_wav,
    SpeechRecognitionResult,
)
from sebek.utils.errors import SpeechError


class TestSpeechRecognitionResult:
    """Test speech recognition result data class."""

    def test_create_result_with_defaults(self):
        """Test creating result with defaults."""
        result = SpeechRecognitionResult(text="hello")
        assert result.text == "hello"
        assert result.confidence is None
        assert result.words is None

    def test_create_result_with_all_fields(self):
        """Test creating result with all fields."""
        words = [{"conf": 0.99, "result": "hello"}]
        vosk_result = {"result": words, "text": "hello"}

        result = SpeechRecognitionResult(
            text="hello",
            confidence=0.95,
            words=words,
            vosk_result=vosk_result,
            audio_path=Path("/tmp/test.wav"),
            timestamp="20260903_120000",
        )

        assert result.text == "hello"
        assert result.confidence == 0.95
        assert len(result.words) == 1


class TestVoskRecognizer:
    """Test Vosk speech recognizer wrapper."""

    @patch("sebek.speech.recognizer.HAS_VOSK", False)
    def test_vosk_not_available_raises_error(self):
        """Test error when Vosk not installed."""
        with pytest.raises(SpeechError):
            VoskRecognizer()

    @patch("sebek.speech.recognizer.HAS_VOSK", True)
    @patch("sebek.speech.recognizer.Model")
    def test_vosk_model_not_found_raises_error(self, mock_model):
        """Test error when model path not found."""
        with pytest.raises(SpeechError):
            VoskRecognizer(model_path=Path("/nonexistent/model"))

    @patch("sebek.speech.recognizer.HAS_VOSK", True)
    @patch("sebek.speech.recognizer.Model")
    def test_vosk_recognizer_initializes(self, mock_model, temp_dir):
        """Test successful Vosk recognizer initialization."""
        model_path = temp_dir / "model"
        model_path.mkdir()

        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance

        with patch("sebek.speech.recognizer.KaldiRecognizer"):
            recognizer = VoskRecognizer(model_path=model_path)
            assert recognizer.model_path == model_path

    @patch("sebek.speech.recognizer.HAS_VOSK", True)
    @patch("sebek.speech.recognizer.Model")
    @patch("sebek.speech.recognizer.KaldiRecognizer")
    def test_accept_waveform(self, mock_kaldi, mock_model, temp_dir):
        """Test accepting waveform data."""
        model_path = temp_dir / "model"
        model_path.mkdir()

        mock_kaldi_instance = MagicMock()
        mock_kaldi_instance.AcceptWaveform.return_value = True
        mock_kaldi.return_value = mock_kaldi_instance

        recognizer = VoskRecognizer(model_path=model_path)
        result = recognizer.accept_waveform(b"\x00\x01\x02\x03")

        assert result is True


class TestTextToSpeech:
    """Test text-to-speech wrapper."""

    @patch("sebek.speech.recognizer.HAS_TTS", False)
    def test_tts_disabled_when_unavailable(self):
        """Test TTS disabled when pyttsx3 unavailable."""
        tts = TextToSpeech(enable=True)
        assert not tts.enabled

    @patch("sebek.speech.recognizer.HAS_TTS", True)
    @patch("sebek.speech.recognizer.pyttsx3.init")
    def test_tts_initializes(self, mock_init):
        """Test TTS engine initialization."""
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine

        tts = TextToSpeech(enable=True)
        assert tts.enabled
        assert tts.engine == mock_engine

    @patch("sebek.speech.recognizer.HAS_TTS", True)
    @patch("sebek.speech.recognizer.pyttsx3.init")
    def test_tts_speak(self, mock_init):
        """Test TTS speak method."""
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine

        tts = TextToSpeech(enable=True)
        tts.speak("Hello SEBEK")

        mock_engine.say.assert_called_once_with("Hello SEBEK")
        mock_engine.runAndWait.assert_called_once()

    @patch("sebek.speech.recognizer.HAS_TTS", False)
    def test_tts_disabled_speak_noop(self):
        """Test speak is no-op when TTS disabled."""
        tts = TextToSpeech(enable=False)
        # Should not raise
        tts.speak("Hello")


class TestSaveAudioToWav:
    """Test audio file saving."""

    def test_save_audio_to_wav_creates_file(self, temp_dir):
        """Test saving audio creates WAV file."""
        output_path = temp_dir / "test.wav"
        audio_bytes = b"\x00\x01\x00\x02\x00\x03\x00\x04"  # 4 int16 samples

        save_audio_to_wav(output_path, audio_bytes)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_save_audio_to_wav_with_custom_params(self, temp_dir):
        """Test saving with custom sample rate and channels."""
        output_path = temp_dir / "test.wav"
        audio_bytes = b"\x00\x01\x00\x02"

        save_audio_to_wav(
            output_path,
            audio_bytes,
            sample_rate=8000,
            channels=2,
        )

        assert output_path.exists()

    def test_save_audio_invalid_path_raises_error(self):
        """Test error when path is invalid."""
        invalid_path = Path("/invalid/path/that/does/not/exist/test.wav")
        audio_bytes = b"\x00\x01"

        with pytest.raises(SpeechError):
            save_audio_to_wav(invalid_path, audio_bytes)
