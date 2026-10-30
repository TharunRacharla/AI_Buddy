import json
import logging
import threading

import pyttsx3
from channels.generic.websocket import WebsocketConsumer

from .features.notes.handler import handle_notes
from .intents import detect_intent
from .slm import ChatGenerationError, generate_reply
from .voice import record_and_transcribe, set_wake_callback, start_wake_word_listener

logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        set_wake_callback(self._on_wake_word)
        start_wake_word_listener()
        logger.info("Desktop client connected")

    def disconnect(self, close_code):
        logger.info("Desktop client disconnected with code %s", close_code)

    def receive(self, text_data):
        try:
            message = json.loads(text_data)
            if not isinstance(message, dict):
                raise ValueError("WebSocket message must be a JSON object")

            msg_type = message.get("type", "")
            data = message.get("data", {})
            if not isinstance(data, dict):
                raise ValueError("WebSocket message data must be an object")

            if msg_type == "voice":
                threading.Thread(target=self.handle_voice, daemon=True).start()
            elif msg_type == "chat":
                self._handle_text(data.get("text", ""), data.get("meta"))
            else:
                self.reply("Unknown message type.")
        except (json.JSONDecodeError, ValueError):
            logger.warning("Received an invalid WebSocket message")
            self.reply("Error: Invalid message format.")
        except Exception:
            logger.exception("Could not process WebSocket message")
            self.reply("An error occurred while processing your request.")

    def handle_intent(self, intent, text, meta=None):
        if intent.startswith("note_"):
            handle_notes(intent, text, meta, self)
            return

        try:
            self.reply(generate_reply(text))
        except ChatGenerationError:
            self.reply("I couldn't generate a reply right now. Please try again.")

    def _handle_text(self, text, meta=None):
        if isinstance(text, str) and text.strip():
            if len(text) > 500:
                self.reply("Messages must be 500 characters or fewer.")
                return
            self.handle_intent(detect_intent(text), text, meta)
        else:
            self.reply("Please enter a valid message.")

    def handle_voice(self):
        text = record_and_transcribe()
        if text:
            self._handle_text(text)
        else:
            self.reply("Sorry, I didn't catch that. Try again!")

    def _send_safe(self, msg_type, data):
        try:
            self.send(text_data=json.dumps({"type": msg_type, "data": data}))
        except Exception:
            logger.warning("Could not send %s message to desktop client", msg_type, exc_info=True)

    def reply(self, text):
        self._send_safe("chat", {"text": text})

    def send_to_electron(self, msg_type, data):
        self._send_safe(msg_type, data)

    def speak(self, text):
        def _speak():
            try:
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception:
                logger.exception("Text-to-speech playback failed")

        threading.Thread(target=_speak, daemon=True).start()

    def agent_message(self, event):
        self.send_to_electron(event["msg_type"], event["data"])

    def _on_wake_word(self):
        logger.info("Starting voice command after wake word")
        self.send_to_electron("status", {
            "state": "working",
            "icon": "🎤",
            "title": "Hey Buddy!",
            "detail": "Listening for your command...",
            "progress": 50,
        })
        threading.Thread(target=self._handle_wake, daemon=True).start()

    def _handle_wake(self):
        try:
            text = record_and_transcribe()
            if text:
                self._handle_text(text)
            else:
                self.reply("Sorry, I didn't catch that. Try again!")
        except Exception:
            logger.exception("Could not process wake-word voice command")
            self.send_to_electron("status", {
                "state": "idle",
                "icon": "❌",
                "title": "Error",
                "detail": "Voice command failed. Please try again.",
                "progress": 0,
            })
