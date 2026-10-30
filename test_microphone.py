import logging

import speech_recognition as sr

logger = logging.getLogger(__name__)


def main():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            logger.info("Listening for a microphone test")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        text = recognizer.recognize_whisper(audio, model="base.en")
        if not text.strip():
            logger.warning("No speech was transcribed")
            return 1

        logger.info("Microphone transcription succeeded")
        return 0
    except Exception:
        logger.exception("Microphone test failed")
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
