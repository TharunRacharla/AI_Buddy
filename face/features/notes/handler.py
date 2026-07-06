from face.features.notes.models import Note
from face.features.notes.templates import notes_panel

def handle_notes(intent, text, meta, consumer):

    if intent == "note_create":
        consumer.send_to_electron("custom", {
            "html": notes_panel(new=True)
        })
        consumer.speak("Opening a new note.")

    elif intent == "note_save":
        if meta:
            title   = meta.get("title", "").strip()
            content = meta.get("content", "").strip()
            note_id = meta.get("note_id")

            if note_id and note_id != "new":
                note = Note.objects.get(id=note_id)
                note.title   = title
                note.content = content
                note.save()
                consumer.speak("Note updated.")
            else:
                note = Note.objects.create(title=title, content=content)
                consumer.speak("Note saved.")

            consumer.send_to_electron("custom", {
                "html": notes_panel(note=note)
            })

    elif intent == "note_delete":
        if meta and meta.get("note_id") and meta["note_id"] != "new":
            Note.objects.filter(id=meta["note_id"]).delete()
            # show next available note or empty panel
            note = Note.objects.first()
            consumer.speak("Note deleted.")
            consumer.send_to_electron("custom", {
                "html": notes_panel(note=note, new=not note)
            })

    elif intent == "note_read":
        notes = Note.objects.all()
        if notes.exists():
            note = notes.first()
            consumer.speak(note.content or note.title or "Note is empty.")
            consumer.send_to_electron("custom", {
                "html": notes_panel(note=note)
            })
        else:
            consumer.reply("You have no notes yet!")

    elif intent == "note_next":
        _navigate(meta, consumer, direction="next")

    elif intent == "note_prev":
        _navigate(meta, consumer, direction="prev")

    elif intent == "note_close":
        consumer.send_to_electron("chat", {"text": "Closed notes!"})


def _navigate(meta, consumer, direction):
    if not meta or not meta.get("note_id"):
        consumer.reply("No note is open.")
        return

    current_id = meta.get("note_id")
    notes = list(Note.objects.values_list("id", flat=True))

    if not notes or current_id == "new":
        consumer.reply("No notes to navigate.")
        return

    try:
        idx = notes.index(int(current_id))
        if direction == "next":
            idx = (idx + 1) % len(notes)
        else:
            idx = (idx - 1) % len(notes)
        note = Note.objects.get(id=notes[idx])
        consumer.send_to_electron("custom", {"html": notes_panel(note=note)})
    except (ValueError, Note.DoesNotExist):
        consumer.reply("Could not navigate notes.")








"""
class design for Notes

attribute and behaviour

Attributes:
 -- title
 -- content
 -- creation time

Behaviour:
 -- Add note
 -- update_note
 -- Remove\delete note
 -- Navigate through notes
 -- read note

import datetime
 class Note:
    def __init__(self):
        self.creation_time = str(datetime.datetime.now())
    
    
 """