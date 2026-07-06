def notes_panel(note=None, new=False):
    title   = note.title   if note and not new else ""
    content = note.content if note and not new else ""
    note_id = note.id      if note and not new else "new"

    return f"""
    <div style="display:flex; flex-direction:column; height:100%; gap:8px; padding:12px;">
        <input id="note-title" value="{title}" placeholder="Title..."
            style="border:1.5px solid #E8F5B0; border-radius:10px; padding:8px 12px;
                   font-size:13px; font-family:Nunito,sans-serif; font-weight:700;
                   background:#FAFFF0; outline:none; color:#2D2D2D;"/>

        <textarea id="note-content" placeholder="Start typing your note..."
            style="flex:1; border:1.5px solid #E8F5B0; border-radius:10px;
                   padding:10px 12px; font-size:12.5px; font-family:'Nunito Sans',sans-serif;
                   background:#FAFFF0; outline:none; resize:none; color:#2D2D2D;
                   line-height:1.6;">{content}</textarea>

        <div style="display:flex; gap:6px;">
            <button onclick="window.noteAction('prev', '{note_id}')"
                style="flex:1; padding:7px; border:none; border-radius:9px;
                       background:#F0F0F0; font-family:Nunito,sans-serif;
                       font-weight:700; font-size:11px; cursor:pointer;">◀ Prev</button>

            <button onclick="window.noteAction('save', '{note_id}')"
                style="flex:2; padding:7px; border:none; border-radius:9px;
                       background:#C8F135; font-family:Nunito,sans-serif;
                       font-weight:700; font-size:11px; cursor:pointer;">💾 Save</button>

            <button onclick="window.noteAction('next', '{note_id}')"
                style="flex:1; padding:7px; border:none; border-radius:9px;
                       background:#F0F0F0; font-family:Nunito,sans-serif;
                       font-weight:700; font-size:11px; cursor:pointer;">Next ▶</button>
        </div>

        <button onclick="window.window.noteAction('delete', '{note_id}')"
            style="padding:7px; border:none; border-radius:9px;
                   background:#FFE0E0; font-family:Nunito,sans-serif;
                   font-weight:700; font-size:11px; cursor:pointer; color:#CC4444;">
            🗑 Delete this note</button>
    </div>
    """