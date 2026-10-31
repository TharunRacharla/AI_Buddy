# AI Buddy

AI Buddy is a desktop assistant built around a voice-to-action loop. It combines an always-available Electron interface with a Django backend, letting you interact by voice or text and manage notes through the assistant.

## What it does

- **Voice and text interaction:** Start a voice interaction with “Hey Buddy” or send a message through chat.
- **Real-time desktop assistant:** The Electron app and backend stay connected so the assistant can respond and update the interface live.
- **Local AI models:** Whisper transcribes speech, while a Qwen model classifies intents and generates chat replies.
- **Note management:** Create, read, navigate, update, and delete notes through voice or chat.
- **Desktop-first experience:** A compact assistant panel brings chat, voice input, activity status, and notes together.

## Current scope

Chat, voice, and notes are the implemented assistant flows. File management, browsers, and media players are not implemented yet.
