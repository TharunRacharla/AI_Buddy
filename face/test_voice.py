from unittest.mock import Mock, patch

from django.test import SimpleTestCase
import speech_recognition as sr

from .voice import _transcribe


class VoiceTranscriptionTests(SimpleTestCase):
    @patch("face.voice._get_whisper_model")
    def test_transcribe_uses_cached_whisper_model(self, get_model):
        whisper_model = Mock()
        whisper_model.transcribe.return_value = {"text": " hello "}
        get_model.return_value = whisper_model
        audio = sr.AudioData(b"\0" * 32000, sample_rate=16000, sample_width=2)

        transcription = _transcribe(audio, "tiny.en")

        self.assertEqual(transcription, "hello")
        get_model.assert_called_once_with("tiny.en")
        whisper_model.transcribe.assert_called_once()
