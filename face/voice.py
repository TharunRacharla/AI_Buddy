import logging
import threading
import time

import numpy as np
import speech_recognition as sr

logger = logging.getLogger(__name__)

_wake_recognizer = sr.Recognizer()
_cmd_recognizer = sr.Recognizer()

_wake_callback = None
_listener_started = False
_listener_lock = threading.Lock()
_model_lock = threading.Lock()
_record_lock = threading.Lock()
_microphone_lock = threading.Lock()
_whisper_models = {}

_mic_free = threading.Event()
_mic_free.set()


def _get_whisper_model(model_name):
    with _model_lock:
        if model_name not in _whisper_models:
            import whisper

            logger.info("Loading Whisper model %s", model_name)
            _whisper_models[model_name] = whisper.load_model(model_name)
            logger.info("Whisper model %s is ready", model_name)
        return _whisper_models[model_name]


def _transcribe(audio, model_name):
    raw_audio = audio.get_raw_data(convert_rate=16000, convert_width=2)
    waveform = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0
    result = _get_whisper_model(model_name).transcribe(waveform, fp16=False)
    return result["text"].strip()


def set_wake_callback(callback):
    global _wake_callback
    _wake_callback = callback


def start_wake_word_listener():
    global _listener_started
    with _listener_lock:
        if _listener_started:
            logger.debug("Wake-word listener is already running")
            return
        _listener_started = True
        threading.Thread(target=_listen_loop, daemon=True).start()


def _listen_loop():
    logger.info("Wake-word listener started")
    while True:
        _mic_free.wait()

        try:
            with _microphone_lock:
                if not _mic_free.is_set():
                    continue
                with sr.Microphone() as source:
                    _wake_recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = _wake_recognizer.listen(source, timeout=5, phrase_time_limit=4)

            if not _mic_free.is_set():
                continue

            try:
                text = _transcribe(audio, "tiny.en").lower()
                if "hey buddy" in text or "hey body" in text:
                    logger.info("Wake word detected")
                    if _wake_callback:
                        _wake_callback()
            except sr.UnknownValueError:
                logger.debug("Wake-word audio was not understood")
            except Exception:
                logger.exception("Wake-word recognition failed")
                time.sleep(1)

        except sr.WaitTimeoutError:
            logger.debug("Wake-word listening timed out")
        except Exception:
            logger.exception("Wake-word listener failed")
            time.sleep(1)


def record_and_transcribe():
    with _record_lock:
        _mic_free.clear()
        try:
            with _microphone_lock:
                with sr.Microphone() as source:
                    _cmd_recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = _cmd_recognizer.listen(source, timeout=10, phrase_time_limit=15)

            try:
                return _transcribe(audio, "base.en")
            except sr.UnknownValueError:
                logger.info("Command audio was not understood")
                return ""
            except Exception:
                logger.exception("Command transcription failed")
                return ""
        except sr.WaitTimeoutError:
            logger.info("No command was heard before the listening timeout")
            return ""
        except Exception:
            logger.exception("Could not access the microphone")
            return ""
        finally:
            _mic_free.set()
