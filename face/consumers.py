import json, os
import pyttsx3, threading
from channels.generic.websocket import WebsocketConsumer
from .intents import detect_intent
from .features.notes.handler import handle_notes
from .voice import start_wake_word_listener, set_wake_callback, record_and_transcribe


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = "agent"
        self.room_group_name = "agent_room"
        self.accept()

        # start wake word listener and point it to this consumer
        set_wake_callback(self._on_wake_word)
        start_wake_word_listener()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            msg_type = text_data_json.get("type", "")
            data = text_data_json.get("data", {})

            if msg_type == "voice":
                if data.get("audio"):
                    threading.Thread(target=self.handle_voice, args=(data.get("audio"),), daemon=True).start()
            elif msg_type == "chat":
                self._handle_text(data.get("text", ""), data.get("meta"))
            else:
                self.reply("Unknown message type.")
        except json.JSONDecodeError:
            print("Invalid JSON received")
            self.reply("Error: Invalid message format.")
        except Exception as e:
            print(f"Error in receive: {e}")
            self.reply("An error occurred while processing your request.")

    def handle_intent(self, intent, text, meta=None):
        if intent.startswith("note_"):
            handle_notes(intent, text, meta, self)
        else:
            self.reply(f"You said: {text}")

    def _handle_text(self, text, meta=None):
        if isinstance(text, str) and text.strip():
            self.handle_intent(detect_intent(text), text, meta)
        else:
            self.reply("Please enter a valid message.")

    def handle_voice(self, audio_base64):
        text = record_and_transcribe()
        if text:
            self._handle_text(text)
        else:
            self.reply("Sorry, I didn't catch that. Try again!")

    # ── HELPERS ──

    def _send_safe(self, msg_type, data):
        """Send directly over the WebSocket — safe to call from any thread."""
        try:
            self.send(text_data=json.dumps({"type": msg_type, "data": data}))
        except Exception as e:
            print(f"[WARN] _send_safe failed ({msg_type}): {e}")

    def reply(self, text):
        self._send_safe("chat", {"text": text})

    def send_to_electron(self, msg_type, data):
        self._send_safe(msg_type, data)

    def speak(self, text):
        def _speak():
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        threading.Thread(target=_speak, daemon=True).start()

    def agent_message(self, event):
        self.send(text_data=json.dumps({
            "type": event["msg_type"],
            "data": event["data"]
        }))

    def _on_wake_word(self):
        import traceback
        try:
            print("_on_wake_word: entered")

            # notify Electron to show listening state
            try:
                self.send_to_electron("status", {
                    "state":    "working",
                    "icon":     "🎤",
                    "title":    "Hey Buddy!",
                    "detail":   "Listening for your command...",
                    "progress": 50
                })
            except Exception as e:
                print(f"send_to_electron error: {e}")
                traceback.print_exc()

            # record and handle the command in a background thread
            print("_on_wake_word: starting _handle_wake thread")
            t = threading.Thread(target=self._handle_wake, daemon=True)
            t.start()
            print("_on_wake_word: thread started")

        except Exception as e:
            print(f"_on_wake_word exception: {e}")
            traceback.print_exc()

    def _handle_wake(self):
        import traceback
        try:
            print("_handle_wake: entered")
            text = record_and_transcribe()
            print(f"_handle_wake: record_and_transcribe returned: {repr(text)}")
            if text:
                self._handle_text(text)
            else:
                print("_handle_wake: no text transcribed")
                self.reply("Sorry, I didn't catch that. Try again!")

        except Exception as e:
            print(f"_handle_wake exception: {e}")
            traceback.print_exc()
            self.send_to_electron("status", {
                "state": "idle", "icon": "❌",
                "title": "Error", "detail": str(e), "progress": 0
            })