from django.test import SimpleTestCase

from .intents import detect_intent


class IntentDetectionTests(SimpleTestCase):
    def test_note_creation_intent_is_detected(self):
        self.assertEqual(detect_intent("create a new note"), "note_create")

    def test_note_read_intent_is_detected(self):
        self.assertEqual(detect_intent("read my notes"), "note_read")

    def test_unknown_text_falls_back_to_chat(self):
        self.assertEqual(detect_intent("what is the weather"), "chat")

    def test_invalid_input_falls_back_to_chat(self):
        self.assertEqual(detect_intent(None), "chat")
