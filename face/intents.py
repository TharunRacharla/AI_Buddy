def detect_intent(text):
    """Detect intent from user input with lightweight keyword matching first."""
    if not text or not isinstance(text, str):
        return "chat"

    text = text.strip()[:500].lower()
    if not text:
        return "chat"

    keyword_map = {
        "note_create": ("create", "new note", "make note", "add note", "write note"),
        "note_save": ("save", "store", "keep note"),
        "note_delete": ("delete", "remove", "erase"),
        "note_read": ("read", "open note", "show note", "display note"),
        "note_next": ("next note", "next"),
        "note_prev": ("previous note", "previous", "prev", "back"),
        "note_close": ("close note", "close notes", "exit note"),
    }

    for intent, phrases in keyword_map.items():
        if any(phrase in text for phrase in phrases):
            return intent

    try:
        from .slm import classify_intent
        return classify_intent(text)
    except Exception:
        return "chat"

INTENTS = [
    # notes
    "note_create", "note_save", "note_delete",
    "note_read",   "note_next", "note_prev", "note_close",

    # always last
    "chat"
]
