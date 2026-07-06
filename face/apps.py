from django.apps import AppConfig

class FaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'face'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return  # skip on reloader process
        print("Initialising SLM...")
        from .slm import classify_intent
        classify_intent("warmup")
        print("SLM ready!")