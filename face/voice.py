import speech_recognition as sr
import threading
import traceback
import whisper as _whisper  # pre-load models here to avoid mid-conversation RAM spike

_wake_recognizer = sr.Recognizer()   # used only by the wake-word loop
_cmd_recognizer  = sr.Recognizer()   # used only by record_and_transcribe

_wake_callback = None        # will be set by consumer
_listener_started = False    # guard: only one listener thread ever runs

# Pre-load both Whisper models now so they're cached before any call is made.
# base.en is ~150 MB — loading it here prevents a memory spike during the first command.
print("[voice] Pre-loading Whisper models...")
_whisper.load_model("tiny.en")
_whisper.load_model("base.en")
print("[voice] Whisper models ready.")

# _mic_free: SET = mic is available for the wake loop.
#            CLEAR = record_and_transcribe holds the mic; wake loop must wait.
_mic_free = threading.Event()
_mic_free.set()   # mic starts out available

def set_wake_callback(callback):
    global _wake_callback
    _wake_callback = callback

def start_wake_word_listener():
    global _listener_started
    if _listener_started:
        print("[DEBUG] Wake word listener already running, skipping.")
        return
    _listener_started = True
    thread = threading.Thread(target=_listen_loop, daemon=True)
    thread.start()

def _listen_loop():
    print("Wake word listener started...")
    while True:
        # Block here while record_and_transcribe holds the mic (_mic_free is clear).
        # Returns as soon as _mic_free is set (mic available again).
        _mic_free.wait()

        try:
            print("[DEBUG] Listening for wake word...")
            with sr.Microphone() as source:
                _wake_recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = _wake_recognizer.listen(source, timeout=5, phrase_time_limit=4)

            # If the mic was reclaimed while we were listening, discard and yield
            if not _mic_free.is_set():
                continue

            try:
                # tiny model — fast, just for wake word
                text = _wake_recognizer.recognize_whisper(audio, model="tiny.en")
                text = text.lower().strip()
                print(f"Heard: {text}")

                if "hey buddy" in text or "hey body" in text:  # common mishear
                    print("Wake word detected!")
                    if _wake_callback:
                        _wake_callback()

            except sr.UnknownValueError:
                pass  # silence or unclear — keep listening
            except Exception as e:
                print(f"[ERROR] Wake word recognition error: {e}")
                traceback.print_exc()

        except sr.WaitTimeoutError:
            pass  # no speech in timeout window — keep listening
        except Exception as e:
            print(f"[FATAL] Wake listener error: {e}")
            traceback.print_exc()

def record_and_transcribe():
    # Claim the mic: clear the event so the wake loop blocks on _mic_free.wait()
    _mic_free.clear()
    try:
        print("[DEBUG] Starting record_and_transcribe...")
        with sr.Microphone() as source:
            print("Listening for command...")
            _cmd_recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = _cmd_recognizer.listen(source, timeout=10, phrase_time_limit=15)

        try:
            text = _cmd_recognizer.recognize_whisper(audio, model="base.en")
            print(f"Transcribed: {text}")
            return text.strip()
        except sr.WaitTimeoutError:
            print("Transcription error: WaitTimeoutError")
            return ""
        except sr.UnknownValueError:
            print("Transcription error: UnknownValueError")
            return ""
        except Exception as e:
            print(f"Transcription error: {e}")
            traceback.print_exc()
            return ""
    except Exception as e:
        print(f"[FATAL] Microphone or audio error in record_and_transcribe: {e}")
        traceback.print_exc()
        return ""
    finally:
        # Always release the mic back to the wake loop
        _mic_free.set()
        print("[DEBUG] Mic released back to wake listener")