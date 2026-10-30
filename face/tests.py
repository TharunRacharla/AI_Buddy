from unittest.mock import patch

from django.test import SimpleTestCase

from .intents import detect_intent


class IntentDetectionTests(SimpleTestCase):
    def test_note_creation_intent_is_detected(self):
        self.assertEqual(detect_intent("create a new note"), "note_create")

    def test_note_read_intent_is_detected(self):
        self.assertEqual(detect_intent("read my notes"), "note_read")

    @patch("face.slm._generate", return_value="chat")
    def test_unknown_text_falls_back_to_chat(self, _generate):
        self.assertEqual(detect_intent("what is the weather"), "chat")

    @patch("face.slm._generate", return_value="note_read")
    def test_model_classifies_intent(self, _generate):
        self.assertEqual(detect_intent("could you present my collection"), "note_read")

    @patch("face.slm._generate", side_effect=RuntimeError("model unavailable"))
    def test_model_failure_falls_back_to_chat(self, _generate):
        self.assertEqual(detect_intent("please do something unusual"), "chat")

    def test_invalid_input_falls_back_to_chat(self):
        self.assertEqual(detect_intent(None), "chat")
