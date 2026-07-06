def detect_intent(text):
    """Detect intent from user input with proper validation."""
    # Validate and sanitize input
    if not text or not isinstance(text, str):
        return "chat"  # default to chat for invalid input
    
    # Strip whitespace and limit length to 500 characters
    text = text.strip()[:500]
    
    if not text:
        return "chat"  # empty string after stripping
    
    from .slm import classify_intent
    return classify_intent(text)

INTENTS = [
    # notes
    "note_create", "note_save", "note_delete",
    "note_read",   "note_next", "note_prev", "note_close",

    # always last
    "chat"
]
