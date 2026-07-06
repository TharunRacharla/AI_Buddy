import speech_recognition as sr
import traceback

recognizer = sr.Recognizer()

print("Testing microphone and speech recognition...")

try:
    with sr.Microphone() as source:
        print("Please say something...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
        print("Audio captured, recognizing...")
        try:
            text = recognizer.recognize_whisper(audio, model="base.en")
            print(f"Transcribed: {text}")
        except Exception as e:
            print(f"Recognition error: {e}")
            traceback.print_exc()
except Exception as e:
    print(f"Microphone or audio error: {e}")
    traceback.print_exc()

print("Test complete.")
