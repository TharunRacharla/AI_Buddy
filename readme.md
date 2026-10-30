# AI Buddy

AI Buddy is a desktop assistant built around a voice-to-action loop. Instead of living only in a browser tab, it combines an always-available Electron interface with a Django backend over a persistent Channels WebSocket connection. Say the wake word or type a message, and the assistant can respond, use local speech and language models, or open and manage notes in the desktop UI.

## What makes it different

- **Wake-word voice interaction:** A background listener can react to “Hey Buddy,” record a follow-up command, and pass it to the assistant.
- **A live desktop connection:** Django Channels keeps the Electron UI and backend in real-time communication, so replies, status updates, and custom panels can be pushed to the app.
- **Local model workflow:** Whisper handles speech transcription and a Qwen model classifies intents and generates chat replies. Models load when needed, rather than delaying ordinary startup.
- **Actions, not only conversation:** Notes can be created, read, navigated, updated, and deleted through chat or voice commands.
- **A desktop-first UI:** Electron provides a compact assistant panel with chat, activity status, voice input, and note views.

Together, these pieces make AI Buddy an early desktop-agent prototype: voice and text are interfaces to actions, not just ways to send prompts.

## Current scope

Chat, voice, and notes are the implemented assistant flows. The other app categories sometimes associated with desktop assistants—such as file management, browsers, and media players—are not implemented yet.

## Requirements

- Python 3.12 or later
- Node.js and npm
- FFmpeg available on `PATH` for Whisper transcription
- A working microphone and audio output for voice features

## Run locally (Windows)

From the repository root, create and activate a virtual environment, then install the Python packages:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
```

The repository includes a private, ignored `.env` for this local checkout. For a fresh clone, copy `.env.example` to `.env` and replace `DJANGO_SECRET_KEY` with a unique random value before running the app.

In one terminal, start Django:

```powershell
python manage.py runserver 127.0.0.1:8000
```

In another terminal:

```powershell
cd electron_ui
npm install
npm start
```

The Qwen language model and Whisper models are downloaded on first use. Model download and inference require an internet connection initially and can use substantial disk space and memory.

## Configuration

Settings are loaded from the root `.env` file and can also be provided through environment variables. Process environment values take precedence:

- `DJANGO_SECRET_KEY`: persistent secret key; set this for deployments.
- `DJANGO_DEBUG`: defaults to `false`; set it to `true` for the local HTTP runserver shown above.
- `DJANGO_ALLOWED_HOSTS`: comma-separated allowed hosts; defaults to `127.0.0.1,localhost`.
- `DJANGO_CORS_ALLOWED_ORIGINS`: comma-separated HTTP origins; defaults to localhost.
- `DJANGO_LOG_LEVEL`: Python logging level; defaults to `INFO`.
- `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SESSION_COOKIE_SECURE`, and `DJANGO_CSRF_COOKIE_SECURE`: production defaults enable HTTPS redirect, HSTS, and secure cookies.
- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` and `DJANGO_SECURE_HSTS_PRELOAD`: opt in only after confirming every affected hostname is served exclusively over HTTPS.

Set a persistent secret and explicit allowed hosts for deployments. Do not expose the local development server to untrusted networks.

Application logs are written to the console. The manual microphone check is intentionally separate from Django's test suite and can be run with `python test_microphone.py`.
